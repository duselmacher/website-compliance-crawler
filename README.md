# Website Compliance Crawler

Daten-Sammler für Clara (Compliance-Analyse in Claude Projects).

## Was macht dieses Tool?

Der Crawler sammelt strukturierte Daten von Websites:
- Sitemap-basiertes URL-Discovery
- Content-Extraktion (Titel, Headings, Meta, Bilder, Produktdaten)
- Kategorisierung (products, blogs, pages, collections, policies, other)
- Auto-Discovery von Policy-Seiten (Impressum, Datenschutz, AGB, etc.)
- JSON-Export für Clara

**Wichtig:** Der Crawler prüft KEINE Compliance. Er sammelt nur Daten. Clara macht die Analyse.

## Installation

```bash
./setup.sh
# oder manuell:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Nutzung

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Virtual Environment verlassen (wenn fertig)
deactivate
```

### Beispiele

```bash
source venv/bin/activate

# Nur URLs sammeln (schnell)
python crawler.py --domain probiom.com

# Mit Content-Extraktion
python crawler.py --domain probiom.com --extract-content

# Nur bestimmte Kategorien
python crawler.py --domain probiom.com --extract-content --categories products

# Alles AUSSER Blogs
python crawler.py --domain probiom.com --extract-content --exclude blogs

# Mit URL-Limit
python crawler.py --domain probiom.com --extract-content --max-urls 100
```

## Output

JSON-Dateien werden nach `output/` geschrieben (→ Dropbox-Sync).

## Workflow mit Clara

1. Crawler ausführen → JSON generieren
2. JSON zu Clara in Claude Projects hochladen
3. Clara analysiert Compliance (Health Claims, HWG, etc.)

## Entwicklung

Entwickelt mit Claude Code für Water & Salt AG.

## Lizenz

Privat - Manuel Hendel
