# Usage Guide

## Grundlegende Nutzung

### Nur URLs sammeln (schnell)
```bash
python crawler.py --domain probiom.com
```
Gibt eine Übersicht aller URLs in der Sitemap, kategorisiert nach Typ.
Schreibt zusätzlich einen URL-Report als `*_urls.json` nach `output/`.

### Domain-Format
Beides wird akzeptiert:
```bash
python crawler.py --domain probiom.com
python crawler.py --domain https://probiom.com
```

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

## Shop-Type

Policy-Seiten (Impressum, Datenschutz, AGB) sind oft nicht in der Sitemap. Der Crawler prüft bekannte Pfade per HTTP HEAD Request. Mit `--shop-type` steuerst du, welche Pfade geprüft werden:

```bash
# Shopify-Shop (5 Pfade unter /policies/)
python crawler.py --domain probiom.com --shop-type shopify

# WooCommerce-Shop (6 Pfade wie /privacy-policy, /impressum, /agb)
python crawler.py --domain example.com --shop-type woocommerce

# Generisch (11 Pfade, breiter Fächer)
python crawler.py --domain example.com --shop-type generic

# Ohne Angabe: alle bekannten Pfade probieren (Standard)
python crawler.py --domain example.com
```

**Empfehlung:** Wenn du den Shop-Typ kennst, gib ihn an – das spart unnötige HTTP-Requests.

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

> **Hinweis:** `--categories` und `--exclude` können nicht gleichzeitig verwendet werden.

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
├── probiom.com_20251218_143022_urls.json      # Immer
├── probiom.com_20251218_143022_content.json   # Mit --extract-content
└── (weitere Crawl-Ergebnisse)
```

### JSON-Struktur (Content)

Compliance-relevante Felder (Titel, Meta-Description, Headings) stehen **vor** dem Fließtext:

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
      "meta_description": "Kurzbeschreibung für Google",
      "headings": {"h1": ["..."], "h2": ["..."], "h3": ["..."]},
      "full_text": "Kompletter sichtbarer Text der Seite...",
      "images": [{"src": "...", "alt": "...", "title": "..."}],
      "product_info": {"name": "...", "description": "...", "price": "..."},
      "error": null
    }
  ]
}
```

## Workflow mit Clara

1. **Crawl durchführen:**
   ```bash
   python crawler.py --domain probiom.com --extract-content --shop-type shopify --exclude blogs
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
- `--max-urls`, `--categories` und `--exclude` erfordern `--extract-content`
