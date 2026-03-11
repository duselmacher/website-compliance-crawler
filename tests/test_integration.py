"""Integration Tests – End-to-End mit gemocktem HTTP."""

import json
from unittest.mock import Mock, patch

from crawler import crawl_urls_only, crawl_with_content

# Fixture: Minimale Sitemap
SITEMAP_XML = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/products/omega-3</loc></url>
  <url><loc>https://example.com/pages/about</loc></url>
  <url><loc>https://example.com/blogs/news</loc></url>
</urlset>
"""

# Fixture: Minimale HTML-Seite
PAGE_HTML = """\
<html>
<head>
    <title>Test Page</title>
    <meta name="description" content="Test meta description">
</head>
<body>
    <h1>Main Heading</h1>
    <h2>Sub Heading</h2>
    <p>Body text for compliance analysis.</p>
</body>
</html>
"""


def _mock_get(url, **kwargs):
    """Mock für requests.get der Sitemaps zurückgibt."""
    resp = Mock()
    resp.content = SITEMAP_XML
    resp.text = SITEMAP_XML.decode()
    resp.status_code = 200
    resp.raise_for_status = Mock()
    return resp


def _mock_head_no_policies(url, **kwargs):
    """Mock für requests.head – Sitemap gefunden, keine Policies."""
    resp = Mock()
    resp.status_code = 200 if "sitemap.xml" in url else 404
    return resp


def _mock_head_with_privacy(url, **kwargs):
    """Mock für requests.head – Sitemap + privacy-policy gefunden."""
    resp = Mock()
    if "sitemap.xml" in url or "privacy-policy" in url:
        resp.status_code = 200
    else:
        resp.status_code = 404
    return resp


class TestCrawlUrlsOnlyIntegration:
    @patch("src.sitemap_parser.requests.get", side_effect=_mock_get)
    @patch("requests.head", side_effect=_mock_head_no_policies)
    def test_crawls_sitemap_and_saves_json(self, mock_head, mock_get, tmp_path):
        result = crawl_urls_only("example.com", tmp_path, shop_type="shopify")

        assert result['domain'] == "example.com"
        assert result['total_urls'] == 3
        assert len(result['urls']['products']) == 1
        assert len(result['urls']['pages']) == 1
        assert len(result['urls']['blogs']) == 1

        # JSON-Datei wurde geschrieben
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1

        data = json.loads(json_files[0].read_text())
        assert data['domain'] == "example.com"
        assert 'crawled_at' in data

    @patch("src.sitemap_parser.requests.get", side_effect=_mock_get)
    @patch("requests.head", side_effect=_mock_head_with_privacy)
    def test_discovers_policy_urls(self, mock_head, mock_get, tmp_path):
        result = crawl_urls_only("example.com", tmp_path, shop_type="shopify")

        assert any("privacy-policy" in url for url in result['urls']['policies'])
        assert result['total_urls'] == 4  # 3 Sitemap + 1 Policy


class TestCrawlWithContentIntegration:
    @patch("src.content_extractor.time.sleep")
    @patch("src.content_extractor.fetch_html", return_value=PAGE_HTML)
    @patch("src.sitemap_parser.requests.get", side_effect=_mock_get)
    @patch("requests.head", side_effect=_mock_head_no_policies)
    def test_crawls_and_extracts_content(self, mock_head, mock_get,
                                          mock_fetch, mock_sleep, tmp_path):
        urls_data, content_data = crawl_with_content(
            "example.com", tmp_path, shop_type="shopify"
        )

        # URLs gecrawlt
        assert urls_data['total_urls'] == 3

        # Content extrahiert (3 Sitemap-URLs + 1 Homepage)
        assert content_data['total_urls'] == 4
        assert content_data['successful'] == 4
        assert content_data['failed'] == 0

        # Compliance-relevante Felder vorhanden
        first_page = content_data['content'][0]
        assert first_page['title'] == "Test Page"
        assert first_page['meta_description'] == "Test meta description"
        assert first_page['headings']['h1'] == ["Main Heading"]
        assert first_page['headings']['h2'] == ["Sub Heading"]

        # headings kommt vor full_text im JSON
        keys = list(first_page.keys())
        assert keys.index('headings') < keys.index('full_text')

        # JSON-Dateien geschrieben (urls + content)
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 2

    @patch("src.content_extractor.time.sleep")
    @patch("src.content_extractor.fetch_html", return_value=PAGE_HTML)
    @patch("src.sitemap_parser.requests.get", side_effect=_mock_get)
    @patch("requests.head", side_effect=_mock_head_no_policies)
    def test_category_filter(self, mock_head, mock_get,
                              mock_fetch, mock_sleep, tmp_path):
        _, content_data = crawl_with_content(
            "example.com", tmp_path, categories=["products"], shop_type="shopify"
        )

        # Homepage + 1 Produkt
        assert content_data['total_urls'] == 2

    @patch("src.content_extractor.time.sleep")
    @patch("src.content_extractor.fetch_html", return_value=PAGE_HTML)
    @patch("src.sitemap_parser.requests.get", side_effect=_mock_get)
    @patch("requests.head", side_effect=_mock_head_no_policies)
    def test_exclude_filter(self, mock_head, mock_get,
                             mock_fetch, mock_sleep, tmp_path):
        _, content_data = crawl_with_content(
            "example.com", tmp_path, exclude=["blogs"], shop_type="shopify"
        )

        # Homepage + products + pages (3) - blogs excluded
        assert content_data['total_urls'] == 3

    @patch("src.content_extractor.time.sleep")
    @patch("src.content_extractor.fetch_html", return_value=PAGE_HTML)
    @patch("src.sitemap_parser.requests.get", side_effect=_mock_get)
    @patch("requests.head", side_effect=_mock_head_no_policies)
    def test_max_urls_limit(self, mock_head, mock_get,
                             mock_fetch, mock_sleep, tmp_path):
        _, content_data = crawl_with_content(
            "example.com", tmp_path, max_urls=2, shop_type="shopify"
        )

        # Max 2 URLs (Homepage + 1)
        assert content_data['total_urls'] == 2
