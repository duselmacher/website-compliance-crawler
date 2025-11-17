# Development Guide

## Mit Claude Code entwickeln

### Claude Code starten
```bash
cd ~/Development/tools/website-compliance-crawler
claude-code
```

### Plan Mode nutzen
Claude Code hat einen **Plan Mode** für größere Features:

1. **Starte mit einem Plan-Prompt:**
```
   @plan Ich möchte folgendes Feature:
   - Sitemap-Parsing für beliebige Domains
   - Extraktion aller URLs
   - Speicherung als JSON
   
   Erstelle einen Implementierungsplan mit einzelnen Schritten.
```

2. **Claude erstellt einen Plan:**
   - Schritt 1: XML-Parser implementieren
   - Schritt 2: URL-Extraktion
   - Schritt 3: Tests schreiben
   - etc.

3. **Plan Schritt-für-Schritt ausführen:**
```
   @plan execute step 1
```

### Gute Prompts für Claude Code

**✅ GUT - Spezifisch & Context:**
```
Erstelle eine Funktion `parse_sitemap(url)` die:
- Eine XML-Sitemap von der URL lädt
- Alle <loc> URLs extrahiert
- Als Python-Liste zurückgibt
- Fehler mit try/except handhabt
```

**❌ SCHLECHT - Zu vage:**
```
Mach mal einen Sitemap Parser
```

**✅ GUT - Iterativ:**
```
Die parse_sitemap Funktion funktioniert, aber:
- Füge Logging hinzu
- Behandle auch Sitemap-Index (Parent Sitemaps)
- Füge Timeout hinzu (10 Sekunden)
```

## Git Workflow

### Feature entwickeln
```bash
# Neuer Branch
git checkout -b feature/sitemap-parser

# Entwickeln, testen...
git add src/parser.py
git commit -m "Add sitemap parser with XML handling"

# Zurück zu main
git checkout main
git merge feature/sitemap-parser
```

### Commits schreiben
**Format:** `<type>: <kurze Beschreibung>`

- `feat:` Neues Feature
- `fix:` Bugfix
- `docs:` Dokumentation
- `test:` Tests
- `refactor:` Code-Umstrukturierung

**Beispiele:**
```bash
git commit -m "feat: Add sitemap parser with parent sitemap support"
git commit -m "fix: Handle timeout errors in URL fetcher"
git commit -m "docs: Update USAGE.md with new CLI flags"
```

## Testing

### Tests ausführen
```bash
# Alle Tests
pytest

# Spezifischer Test
pytest tests/test_parser.py

# Mit Coverage
pytest --cov=src
```

### Neuen Test schreiben
```python
# tests/test_parser.py
def test_parse_sitemap():
    urls = parse_sitemap("https://example.com/sitemap.xml")
    assert len(urls) > 0
    assert all(url.startswith("http") for url in urls)
```

## Code-Qualität

### Style Guide
- Follow PEP 8
- Docstrings für alle Funktionen
- Type hints wo sinnvoll

### Vor dem Commit
```bash
# Format Code
black src/

# Lint
pylint src/

# Type Check
mypy src/
```
