from src.sitemap_parser import categorize_url


def test_categorize_product_url():
    assert categorize_url("https://example.com/products/omega-3") == "products"


def test_categorize_blog_url_has_priority_over_product_keyword():
    url = "https://example.com/blogs/product-news-update"
    assert categorize_url(url) == "blogs"


def test_categorize_collection_url():
    assert categorize_url("https://example.com/collections/supplements") == "collections"


def test_categorize_pages_url():
    assert categorize_url("https://example.com/pages/about-us") == "pages"


def test_categorize_other_url():
    assert categorize_url("https://example.com/contact") == "other"
