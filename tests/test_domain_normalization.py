import pytest

from crawler import normalize_domain


def test_normalize_domain_without_scheme():
    assert normalize_domain("probiom.com") == "probiom.com"


def test_normalize_domain_with_https_scheme():
    assert normalize_domain("https://probiom.com") == "probiom.com"


def test_normalize_domain_with_http_scheme_and_path():
    assert normalize_domain("http://Example.com/shop") == "example.com"


def test_normalize_domain_with_trailing_slash_and_whitespace():
    assert normalize_domain("  https://PROBIOM.com/  ") == "probiom.com"


def test_normalize_domain_empty_raises_value_error():
    with pytest.raises(ValueError):
        normalize_domain("   ")
