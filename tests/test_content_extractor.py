"""Tests für content_extractor – HTML-Parsing und Datenextraktion."""

from unittest.mock import patch

from bs4 import BeautifulSoup

from src.content_extractor import (
    clean_text,
    extract_content,
    extract_full_text,
    extract_headings,
    extract_images,
    extract_meta_description,
    extract_product_info,
    extract_title,
)


def _soup(html: str) -> BeautifulSoup:
    """Erzeugt ein BeautifulSoup-Objekt aus HTML-String."""
    return BeautifulSoup(html, "html.parser")


# --- clean_text ---

class TestCleanText:
    def test_collapses_whitespace(self):
        assert clean_text("hello   world") == "hello world"

    def test_strips_leading_trailing(self):
        assert clean_text("  hello  ") == "hello"

    def test_normalizes_newlines(self):
        assert clean_text("hello\n\n  world") == "hello world"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_none_returns_empty(self):
        assert clean_text(None) == ""


# --- extract_headings ---

class TestExtractHeadings:
    def test_extracts_h1_h2_h3(self):
        html = "<h1>Title</h1><h2>Sub</h2><h3>Detail</h3>"
        headings = extract_headings(_soup(html))
        assert headings["h1"] == ["Title"]
        assert headings["h2"] == ["Sub"]
        assert headings["h3"] == ["Detail"]

    def test_multiple_headings_same_level(self):
        html = "<h2>First</h2><h2>Second</h2>"
        headings = extract_headings(_soup(html))
        assert headings["h2"] == ["First", "Second"]

    def test_empty_headings_ignored(self):
        html = "<h1></h1><h1>Real</h1>"
        headings = extract_headings(_soup(html))
        assert headings["h1"] == ["Real"]

    def test_no_headings(self):
        html = "<p>Just text</p>"
        headings = extract_headings(_soup(html))
        assert headings == {"h1": [], "h2": [], "h3": []}

    def test_whitespace_in_heading_cleaned(self):
        html = "<h1>  Hello   World  </h1>"
        headings = extract_headings(_soup(html))
        assert headings["h1"] == ["Hello World"]


# --- extract_meta_description ---

class TestExtractMetaDescription:
    def test_standard_meta_description(self):
        html = '<meta name="description" content="Test description">'
        assert extract_meta_description(_soup(html)) == "Test description"

    def test_og_description_fallback(self):
        html = '<meta property="og:description" content="OG desc">'
        assert extract_meta_description(_soup(html)) == "OG desc"

    def test_twitter_description_fallback(self):
        html = '<meta name="twitter:description" content="Tweet desc">'
        assert extract_meta_description(_soup(html)) == "Tweet desc"

    def test_prefers_standard_over_og(self):
        html = """
        <meta name="description" content="Standard">
        <meta property="og:description" content="OG">
        """
        assert extract_meta_description(_soup(html)) == "Standard"

    def test_no_description_returns_empty(self):
        html = "<html><head></head></html>"
        assert extract_meta_description(_soup(html)) == ""

    def test_empty_content_skipped(self):
        html = """
        <meta name="description" content="">
        <meta property="og:description" content="Fallback">
        """
        assert extract_meta_description(_soup(html)) == "Fallback"


# --- extract_title ---

class TestExtractTitle:
    def test_title_tag(self):
        html = "<title>My Page</title>"
        assert extract_title(_soup(html)) == "My Page"

    def test_h1_fallback(self):
        html = "<h1>Heading Title</h1>"
        assert extract_title(_soup(html)) == "Heading Title"

    def test_og_title_fallback(self):
        html = '<meta property="og:title" content="OG Title">'
        assert extract_title(_soup(html)) == "OG Title"

    def test_prefers_title_over_h1(self):
        html = "<title>Title Tag</title><h1>H1 Text</h1>"
        assert extract_title(_soup(html)) == "Title Tag"

    def test_no_title_returns_empty(self):
        html = "<p>No title here</p>"
        assert extract_title(_soup(html)) == ""


# --- extract_full_text ---

class TestExtractFullText:
    def test_extracts_body_text(self):
        html = "<body><p>Hello World</p></body>"
        text = extract_full_text(_soup(html))
        assert "Hello World" in text

    def test_strips_scripts_and_styles(self):
        html = """
        <body>
            <script>var x = 1;</script>
            <style>.foo { color: red; }</style>
            <p>Visible text</p>
        </body>
        """
        text = extract_full_text(_soup(html))
        assert "Visible text" in text
        assert "var x" not in text
        assert "color" not in text

    def test_strips_noscript(self):
        html = "<body><noscript>No JS</noscript><p>Content</p></body>"
        text = extract_full_text(_soup(html))
        assert "No JS" not in text
        assert "Content" in text

    def test_fallback_without_body(self):
        html = "<p>No body tag</p>"
        text = extract_full_text(_soup(html))
        assert "No body tag" in text


# --- extract_images ---

class TestExtractImages:
    def test_extracts_image_attributes(self):
        html = '<img src="https://example.com/img.jpg" alt="Test" title="Title">'
        images = extract_images(_soup(html), "https://example.com")
        assert len(images) == 1
        assert images[0]["src"] == "https://example.com/img.jpg"
        assert images[0]["alt"] == "Test"
        assert images[0]["title"] == "Title"

    def test_resolves_relative_urls(self):
        html = '<img src="/images/photo.jpg" alt="Photo">'
        images = extract_images(_soup(html), "https://example.com/page")
        assert images[0]["src"] == "https://example.com/images/photo.jpg"

    def test_skips_images_without_src(self):
        html = '<img alt="No source">'
        images = extract_images(_soup(html), "https://example.com")
        assert len(images) == 0

    def test_keeps_data_urls_as_is(self):
        html = '<img src="data:image/png;base64,abc" alt="Data">'
        images = extract_images(_soup(html), "https://example.com")
        assert images[0]["src"].startswith("data:")

    def test_multiple_images(self):
        html = '<img src="/a.jpg" alt="A"><img src="/b.jpg" alt="B">'
        images = extract_images(_soup(html), "https://example.com")
        assert len(images) == 2


# --- extract_product_info ---

class TestExtractProductInfo:
    def test_extracts_schema_org_product(self):
        html = """
        <div itemtype="https://schema.org/Product">
            <span itemprop="name">Omega-3</span>
            <span itemprop="description">Premium Fish Oil</span>
            <span itemprop="price">29.99</span>
        </div>
        """
        info = extract_product_info(_soup(html))
        assert info["name"] == "Omega-3"
        assert info["description"] == "Premium Fish Oil"
        assert info["price"] == "29.99"

    def test_og_fallback_for_name_and_description(self):
        html = """
        <meta property="og:title" content="Product Name">
        <meta property="og:description" content="Product Desc">
        """
        info = extract_product_info(_soup(html))
        assert info["name"] == "Product Name"
        assert info["description"] == "Product Desc"

    def test_no_product_info_returns_empty_fields(self):
        html = "<p>No product</p>"
        info = extract_product_info(_soup(html))
        assert info["name"] == ""
        assert info["description"] == ""
        assert info["price"] == ""


# --- extract_content (Integration) ---

class TestExtractContent:
    @patch("src.content_extractor.fetch_html")
    def test_returns_structured_result(self, mock_fetch):
        mock_fetch.return_value = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test meta">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Sub Heading</h2>
            <p>Body text content</p>
            <img src="https://example.com/img.jpg" alt="Photo">
        </body>
        </html>
        """
        result = extract_content("https://example.com/test")

        assert result["url"] == "https://example.com/test"
        assert result["title"] == "Test Page"
        assert result["meta_description"] == "Test meta"
        assert result["headings"]["h1"] == ["Main Heading"]
        assert result["headings"]["h2"] == ["Sub Heading"]
        assert "Body text content" in result["full_text"]
        assert len(result["images"]) == 1
        assert result["error"] is None

    @patch("src.content_extractor.fetch_html")
    def test_headings_before_full_text_in_keys(self, mock_fetch):
        """Headings und meta_description sollen vor full_text kommen (Compliance-Relevanz)."""
        mock_fetch.return_value = "<html><body><h1>Test</h1><p>Text</p></body></html>"
        result = extract_content("https://example.com")
        keys = list(result.keys())
        assert keys.index("meta_description") < keys.index("full_text")
        assert keys.index("headings") < keys.index("full_text")

    @patch("src.content_extractor.fetch_html")
    def test_error_handling(self, mock_fetch):
        mock_fetch.side_effect = Exception("Connection failed")
        result = extract_content("https://example.com/broken")
        assert result["error"] == "Connection failed"
        assert result["url"] == "https://example.com/broken"
        assert result["title"] == ""
