# Offene Aufgaben

## Tests
- [x] Tests für sitemap_parser.py (parse_sitemap, parse_sitemap_index, categorize_url, find_sitemap_url)
- [x] Tests für content_extractor.py (clean_text, extract_headings, extract_meta_description, extract_title, extract_full_text, extract_images, extract_product_info, extract_content)
- [x] Mock-HTTP-Responses für alle Netzwerk-Calls
- [x] Integration Tests (End-to-End crawl_urls_only und crawl_with_content mit Mocks)

## Code-Qualität
- [x] Linting eingerichtet (ruff – ersetzt black/pylint, schneller und einfacher)
- [x] pyproject.toml mit pytest- und ruff-Konfiguration
- [x] `sys.path.insert` bereinigt (nutzt jetzt project root statt src/, konsistente `from src.*` Imports)

## Features
- [ ] Retry-Logik bei fehlgeschlagenen HTTP-Requests
- [ ] Granulare Fortschrittsanzeige im Web-Interface (URL-für-URL statt nur Endstatistik)
- [x] Policy-Pfade für Shopify, WooCommerce und generisch – steuerbar via `--shop-type`
- [x] Web-Interface (Flask + SSE, localhost:8080)
- [x] Separate Copy-Buttons für URLs JSON und Content JSON
- [x] Clipboard-Fallback für localhost (textarea + execCommand)
