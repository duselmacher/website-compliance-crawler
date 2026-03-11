# Changelog

## 2026-03-11
- Projekt-Init: CLAUDE.md und docs/-Struktur (decisions, todo, ideas, changelog, sessions/) angelegt
- JSON-Reihenfolge: headings und meta_description jetzt vor full_text (Compliance-Relevanz)
- Tests: 98 Tests total – sitemap_parser und content_extractor vollständig mit Mocks getestet
- Linting: ruff eingerichtet, alle Import-Sortierungen und unused-Variablen gefixt
- pyproject.toml mit pytest- und ruff-Konfiguration angelegt
- Policy-Discovery: Shopify, WooCommerce und generische Pfade, steuerbar via `--shop-type`
- Integration Tests: End-to-End Tests für crawl_urls_only und crawl_with_content
- sys.path.insert bereinigt: project root statt src/, konsistente `from src.*` Imports
- Inline `import time` nach oben verschoben für sauberes Mocking
- README.md komplett überarbeitet: alle CLI-Optionen, Shop-Type-Erklärung, JSON-Struktur
- **Web-Interface:** Flask + SSE auf localhost:8080, Dark Theme, Live-Crawl-Streaming
- Kategorie-Filter-Bug gefixt (Checkboxes starteten checked statt unchecked)
- Clipboard-Fix: Fallback via textarea+execCommand für localhost ohne HTTPS
- Separate Copy-Buttons für URLs JSON und Content JSON
- Backend gibt urls_file und content_file separat zurück
- README mit Web-Interface-Workflow aktualisiert

## 2025-02-14
- Tests für Domain-Normalisierung, URL-Kategorisierung und CLI-Validierung hinzugefügt
- Docs und Crawler-Verhalten gehärtet

## 2025-01-03
- venv Aktivierung/Deaktivierung in README dokumentiert

## 2024-12-19
- Auto-Discovery von Policy-Seiten (nicht in Sitemap)
- Policy-Seiten Feature dokumentiert
