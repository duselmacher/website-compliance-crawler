# Development Guide

## Mit Claude Code entwickeln

```bash
cd ~/Development/tools/website-compliance-crawler
claude
```

## Git Workflow

### Feature entwickeln
```bash
git checkout -b feature/mein-feature
# Entwickeln...
git add .
git commit -m "feat: Beschreibung"
git checkout main
git merge feature/mein-feature
git push
```

### Commit-Format
- `feat:` Neues Feature
- `fix:` Bugfix
- `docs:` Dokumentation
- `refactor:` Code-Umstrukturierung

## Code-Struktur

```
crawler.py              # CLI-Haupteinstieg
src/
├── sitemap_parser.py   # Sitemap-Discovery & URL-Kategorisierung
└── content_extractor.py # HTML-Parsing & Content-Extraktion
```

## Testen

```bash
source venv/bin/activate

# Unit Tests
pytest -q

# Manueller Schnelltest: nur URLs
python crawler.py --domain probiom.com

# Manueller Volltest: mit Content
python crawler.py --domain probiom.com --extract-content --max-urls 5
```

## Dependencies

```bash
pip install -r requirements.txt
```

Aktuell nur: `requests`, `beautifulsoup4`
Aktuell für Tests zusätzlich: `pytest`
