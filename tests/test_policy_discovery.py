"""Tests für Policy-Discovery – Shop-spezifische Policy-Pfade."""

from unittest.mock import Mock, patch

from crawler import (
    POLICY_PATHS,
    VALID_SHOP_TYPES,
    discover_policy_urls,
    get_policy_paths,
)


class TestGetPolicyPaths:
    def test_shopify_returns_shopify_paths(self):
        paths = get_policy_paths('shopify')
        assert paths == POLICY_PATHS['shopify']
        assert '/policies/privacy-policy' in paths

    def test_woocommerce_returns_woocommerce_paths(self):
        paths = get_policy_paths('woocommerce')
        assert paths == POLICY_PATHS['woocommerce']
        assert '/privacy-policy' in paths

    def test_generic_returns_generic_paths(self):
        paths = get_policy_paths('generic')
        assert paths == POLICY_PATHS['generic']
        assert '/impressum' in paths

    def test_none_returns_all_paths_deduplicated(self):
        paths = get_policy_paths(None)
        # Alle Pfade aus allen Shop-Typen enthalten
        for shop_paths in POLICY_PATHS.values():
            for path in shop_paths:
                assert path in paths
        # Keine Duplikate
        assert len(paths) == len(set(paths))

    def test_unknown_shop_type_falls_back_to_generic(self):
        paths = get_policy_paths('unknown_shop')
        assert paths == POLICY_PATHS['generic']

    def test_valid_shop_types_matches_policy_paths_keys(self):
        assert set(VALID_SHOP_TYPES) == set(POLICY_PATHS.keys())


class TestDiscoverPolicyUrls:
    @patch("crawler.requests.head")
    def test_finds_existing_policy_urls(self, mock_head):
        mock_head.return_value = Mock(status_code=200)
        urls = discover_policy_urls("example.com", "shopify")
        assert len(urls) == len(POLICY_PATHS['shopify'])
        assert all(u.startswith("https://example.com/") for u in urls)

    @patch("crawler.requests.head")
    def test_skips_non_200_responses(self, mock_head):
        mock_head.return_value = Mock(status_code=404)
        urls = discover_policy_urls("example.com", "shopify")
        assert urls == []

    @patch("crawler.requests.head")
    def test_handles_request_exceptions(self, mock_head):
        import requests
        mock_head.side_effect = requests.RequestException("timeout")
        urls = discover_policy_urls("example.com", "shopify")
        assert urls == []

    @patch("crawler.requests.head")
    def test_mixed_results(self, mock_head):
        """Nur existierende URLs werden zurückgegeben."""
        def side_effect(url, **kwargs):
            resp = Mock()
            resp.status_code = 200 if "privacy" in url else 404
            return resp
        mock_head.side_effect = side_effect
        urls = discover_policy_urls("example.com", "shopify")
        assert len(urls) == 1
        assert "privacy" in urls[0]

    @patch("crawler.requests.head")
    def test_without_shop_type_tries_all_paths(self, mock_head):
        mock_head.return_value = Mock(status_code=200)
        urls = discover_policy_urls("example.com")
        all_paths = get_policy_paths(None)
        assert len(urls) == len(all_paths)
