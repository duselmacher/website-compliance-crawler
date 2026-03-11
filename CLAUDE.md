# Website Compliance Crawler

CLI-Tool und Web-Interface das Websites crawlt und strukturierte JSON-Daten für Clara (Compliance-Analyse in Claude Projects) sammelt. Für Water & Salt AG.

## Tech-Stack

- **Sprache:** Python 3.14 (venv)
- **Dependencies:** requests, beautifulsoup4, flask, pytest, ruff
- **Output:** JSON nach `output/` (Symlink → Dropbox)
- **Kein Deployment** – lokales Tool, wird direkt auf macOS ausgeführt

## Projektstruktur

```
app.py                  # Web-Interface (Flask, localhost:8080)
crawler.py              # CLI Entry Point (argparse)
templates/index.html    # Web-UI (Single Page, Tailwind CSS)
src/
├── sitemap_parser.py   # Sitemap-Discovery & URL-Kategorisierung
└── content_extractor.py # HTML-Parsing & Content-Extraktion
tests/                  # pytest Unit Tests
docs/                   # Dokumentation (@docs/)
output/                 # Symlink → Dropbox (nicht in Git)
setup.sh                # venv + pip install
```

## Wichtige Befehle

```bash
# Setup
./setup.sh
# oder: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Web-Interface starten (öffnet Browser automatisch)
python app.py

# CLI: Nur URLs crawlen
python crawler.py --domain example.com

# CLI: Mit Content-Extraktion
python crawler.py --domain example.com --extract-content

# CLI: Kategorien filtern/ausschließen
python crawler.py --domain example.com --extract-content --categories products
python crawler.py --domain example.com --extract-content --exclude blogs,collections

# Tests
source venv/bin/activate && pytest -q

# Linting
source venv/bin/activate && ruff check crawler.py app.py src/ tests/
```

## Architektur

- Sitemap-basiertes URL-Discovery mit automatischer Kategorisierung (products, blogs, pages, collections, policies, other)
- Auto-Discovery von Policy-URLs für Shopify, WooCommerce und generische Shops (`--shop-type`)
- Content-Extraktion: Titel, Meta, Headings, Volltext, Bilder, Produkt-Schema
- JSON-Feld-Reihenfolge: Compliance-relevante Felder (headings, meta_description) vor full_text
- Web-Interface: Flask + SSE für Live-Fortschritt, Browser öffnet sich automatisch
- Output wird per Dropbox-Symlink zu Clara (Claude Projects) transportiert

## Dokumentation

- @docs/SETUP.md – Installation & Symlink-Setup
- @docs/USAGE.md – CLI-Optionen & Workflow mit Clara
- @docs/DEVELOPMENT.md – Git-Workflow & Code-Struktur
- @docs/decisions.md – Architekturentscheidungen
- @docs/todo.md – Offene Aufgaben
- @docs/ideas.md – Verbesserungsideen
