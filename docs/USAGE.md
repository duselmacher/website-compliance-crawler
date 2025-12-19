# Usage Guide

## Grundlegende Nutzung

### Nur URLs sammeln (schnell)
```bash
python crawler.py --domain probiom.com
```
Gibt eine Übersicht aller URLs in der Sitemap, kategorisiert nach Typ.

### Mit Content-Extraktion
```bash
python crawler.py --domain probiom.com --extract-content
```
Crawlt alle URLs und extrahiert:
- Titel und Meta-Description
- Headings (H1, H2, H3)
- Volltext
- Bilder mit Alt-Text
- Produkt-Schema-Daten (wenn vorhanden)

## Filter-Optionen

### Nur bestimmte Kategorien (inklusiv)
```bash
# Nur Produkte
python crawler.py --domain probiom.com --extract-content --categories products

# Produkte und Pages
python crawler.py --domain probiom.com --extract-content --categories products,pages
```

### Kategorien ausschließen (exklusiv)
```bash
# Alles ausser Blogs
python crawler.py --domain probiom.com --extract-content --exclude blogs

# Alles ausser Blogs und Collections
python crawler.py --domain probiom.com --extract-content --exclude blogs,collections
```

**Verfügbare Kategorien:** `products`, `blogs`, `pages`, `collections`, `policies`, `other`

> **Hinweis:** `policies` wird automatisch entdeckt (Shopify-Seiten wie Impressum, Datenschutz, AGB sind oft nicht in der Sitemap).

### URL-Limit
```bash
python crawler.py --domain probiom.com --extract-content --max-urls 100
```

### Eigenes Output-Verzeichnis
```bash
python crawler.py --domain probiom.com --output /pfad/zum/ordner
```

## Output-Struktur

```
output/
├── probiom.com_20251218_143022_content.json   # Mit --extract-content
└── (weitere Crawl-Ergebnisse)
```

### JSON-Struktur (Content)
```json
{
  "domain": "probiom.com",
  "crawled_at": "2025-12-18T14:30:22",
  "total_urls": 50,
  "successful": 48,
  "failed": 2,
  "content": [
    {
      "url": "https://probiom.com/products/example",
      "title": "Produkt-Titel",
      "meta_description": "...",
      "headings": {"h1": [...], "h2": [...], "h3": [...]},
      "full_text": "...",
      "images": [...],
      "product_info": {...},
      "error": null
    }
  ]
}
```

## Workflow mit Clara

1. **Crawl durchführen:**
   ```bash
   python crawler.py --domain probiom.com --extract-content --exclude blogs
   ```

2. **JSON finden:**
   - Output liegt in `output/` (→ Dropbox-Sync)

3. **Zu Clara hochladen:**
   - Öffne Claude Projects
   - Upload die JSON-Datei
   - "Clara, analysiere diese Website auf Health Claims Verstöße"

## Hinweise

- Homepage wird IMMER mitgecrawlt (auch bei Filtern)
- 0.5s Pause zwischen Requests (Rate-Limiting)
- Timeout: 10s für Sitemaps, 15s für Content
