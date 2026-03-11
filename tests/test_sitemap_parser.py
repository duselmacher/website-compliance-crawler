"""Tests für sitemap_parser – XML-Parsing und URL-Kategorisierung."""

import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch

import pytest
import requests

from src.sitemap_parser import (
    categorize_url,
    find_sitemap_url,
    parse_sitemap,
    parse_sitemap_index,
)

# --- Fixtures: XML-Beispiele ---

SITEMAP_XML = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/products/omega-3</loc></url>
  <url><loc>https://example.com/pages/about</loc></url>
  <url><loc>https://example.com/blogs/news</loc></url>
</urlset>
"""

SITEMAP_XML_NO_NS = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url><loc>https://example.com/page1</loc></url>
  <url><loc>https://example.com/page2</loc></url>
</urlset>
"""

SITEMAP_INDEX_XML = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example.com/sitemap-products.xml</loc></sitemap>
  <sitemap><loc>https://example.com/sitemap-pages.xml</loc></sitemap>
</sitemapindex>
"""

SITEMAP_INDEX_XML_NO_NS = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex>
  <sitemap><loc>https://example.com/sitemap-a.xml</loc></sitemap>
</sitemapindex>
"""

EMPTY_SITEMAP_XML = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>
"""


def _mock_response(content, status_code=200):
    """Erzeugt ein Mock-Response-Objekt."""
    resp = Mock()
    resp.content = content
    resp.status_code = status_code
    resp.raise_for_status = Mock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
    return resp


# --- parse_sitemap ---

class TestParseSitemap:
    @patch("src.sitemap_parser.requests.get")
    def test_parses_urls_with_namespace(self, mock_get):
        mock_get.return_value = _mock_response(SITEMAP_XML)
        urls = parse_sitemap("https://example.com/sitemap.xml")
        assert len(urls) == 3
        assert "https://example.com/products/omega-3" in urls
        assert "https://example.com/pages/about" in urls

    @patch("src.sitemap_parser.requests.get")
    def test_parses_urls_without_namespace(self, mock_get):
        mock_get.return_value = _mock_response(SITEMAP_XML_NO_NS)
        urls = parse_sitemap("https://example.com/sitemap.xml")
        assert len(urls) == 2

    @patch("src.sitemap_parser.requests.get")
    def test_empty_sitemap_returns_empty_list(self, mock_get):
        mock_get.return_value = _mock_response(EMPTY_SITEMAP_XML)
        urls = parse_sitemap("https://example.com/sitemap.xml")
        assert urls == []

    @patch("src.sitemap_parser.requests.get")
    def test_invalid_xml_raises_parse_error(self, mock_get):
        mock_get.return_value = _mock_response(b"<broken xml")
        with pytest.raises(ET.ParseError):
            parse_sitemap("https://example.com/sitemap.xml")

    @patch("src.sitemap_parser.requests.get")
    def test_timeout_raises_request_exception(self, mock_get):
        mock_get.side_effect = requests.Timeout()
        with pytest.raises(requests.RequestException, match="Timeout"):
            parse_sitemap("https://example.com/sitemap.xml")

    @patch("src.sitemap_parser.requests.get")
    def test_404_raises_request_exception(self, mock_get):
        mock_get.return_value = _mock_response(b"", status_code=404)
        with pytest.raises(requests.RequestException, match="404"):
            parse_sitemap("https://example.com/sitemap.xml")


# --- parse_sitemap_index ---

class TestParseSitemapIndex:
    @patch("src.sitemap_parser.requests.get")
    def test_parses_child_sitemaps_with_namespace(self, mock_get):
        mock_get.return_value = _mock_response(SITEMAP_INDEX_XML)
        urls = parse_sitemap_index("https://example.com/sitemap.xml")
        assert len(urls) == 2
        assert "https://example.com/sitemap-products.xml" in urls

    @patch("src.sitemap_parser.requests.get")
    def test_parses_child_sitemaps_without_namespace(self, mock_get):
        mock_get.return_value = _mock_response(SITEMAP_INDEX_XML_NO_NS)
        urls = parse_sitemap_index("https://example.com/sitemap.xml")
        assert len(urls) == 1

    @patch("src.sitemap_parser.requests.get")
    def test_regular_sitemap_returns_empty_list(self, mock_get):
        mock_get.return_value = _mock_response(SITEMAP_XML)
        urls = parse_sitemap_index("https://example.com/sitemap.xml")
        assert urls == []


# --- categorize_url ---

class TestCategorizeUrl:
    @pytest.mark.parametrize("path,expected", [
        ("/products/omega-3", "products"),
        ("/product/omega-3", "products"),
        ("/blogs/news", "blogs"),
        ("/blog/post-1", "blogs"),
        ("/artikel/gesundheit", "blogs"),
        ("/news/update", "blogs"),
        ("/collections/supplements", "collections"),
        ("/collection/all", "collections"),
        ("/kategorie/vitamine", "collections"),
        ("/category/health", "collections"),
        ("/pages/about", "pages"),
        ("/page/contact", "pages"),
        ("/seite/impressum", "pages"),
        ("/contact", "other"),
        ("/", "other"),
    ])
    def test_categorizes_by_path(self, path, expected):
        assert categorize_url(f"https://example.com{path}") == expected

    def test_blog_takes_priority_over_product_in_path(self):
        """Blog-URLs mit 'product' im Slug sollen als Blog kategorisiert werden."""
        assert categorize_url("https://example.com/blogs/product-tests") == "blogs"


# --- find_sitemap_url ---

class TestFindSitemapUrl:
    @patch("src.sitemap_parser.requests.head")
    def test_finds_standard_sitemap(self, mock_head):
        mock_head.return_value = Mock(status_code=200)
        url = find_sitemap_url("example.com")
        assert url == "https://example.com/sitemap.xml"

    @patch("src.sitemap_parser.requests.head")
    def test_finds_sitemap_index(self, mock_head):
        def side_effect(url, **kwargs):
            resp = Mock()
            resp.status_code = 200 if "sitemap_index" in url else 404
            return resp
        mock_head.side_effect = side_effect
        url = find_sitemap_url("example.com")
        assert "sitemap_index" in url

    @patch("src.sitemap_parser.requests.head")
    def test_raises_when_no_sitemap_found(self, mock_head):
        mock_head.return_value = Mock(status_code=404)
        with pytest.raises(requests.RequestException, match="Keine Sitemap"):
            find_sitemap_url("example.com")

    @patch("src.sitemap_parser.requests.head")
    def test_strips_trailing_slash_from_domain(self, mock_head):
        mock_head.return_value = Mock(status_code=200)
        url = find_sitemap_url("https://example.com/")
        assert url == "https://example.com/sitemap.xml"
