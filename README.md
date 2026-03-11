# Website Compliance Crawler

Daten-Sammler für Clara (Compliance-Analyse in Claude Projects).

## Was macht dieses Tool?

Der Crawler sammelt strukturierte Daten von Websites:
- Sitemap-basiertes URL-Discovery
- Content-Extraktion (Titel, Headings, Meta-Description, Bilder, Produktdaten)
- Kategorisierung (products, blogs, pages, collections, policies, other)
- Auto-Discovery von Policy-Seiten (Impressum, Datenschutz, AGB, etc.)
- Shop-spezifische Policy-Erkennung (Shopify, WooCommerce, generisch)
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

## Web-Interface (empfohlen)

```bash
source venv/bin/activate
python app.py
```

Öffnet automatisch den Browser auf `http://localhost:8080`. Domain eingeben, Optionen wählen, Crawl starten. Live-Fortschritt und Ergebnisse direkt im Browser.

## CLI-Nutzung

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Virtual Environment verlassen (wenn fertig)
deactivate
```

### Alle CLI-Optionen

| Option | Beschreibung |
|--------|-------------|
| `--domain` | **(Pflicht)** Domain zum Crawlen, mit oder ohne Schema |
| `--extract-content` | Extrahiert Titel, Headings, Meta, Volltext, Bilder, Produktdaten |
| `--shop-type` | Shop-System: `shopify`, `woocommerce` oder `generic` (siehe unten) |
| `--categories` | Nur diese Kategorien crawlen (kommasepariert) |
| `--exclude` | Diese Kategorien ausschließen (kommasepariert) |
| `--max-urls` | Maximale Anzahl URLs für Content-Extraktion |
| `--output` | Output-Verzeichnis (Standard: `./output`) |

### Beispiele

```bash
source venv/bin/activate

# Nur URLs sammeln (schnell)
python crawler.py --domain probiom.com

# Domain mit Schema geht auch
python crawler.py --domain https://probiom.com

# Mit Content-Extraktion
python crawler.py --domain probiom.com --extract-content

# Shopify-Shop (prüft nur Shopify-Policy-Pfade)
python crawler.py --domain probiom.com --shop-type shopify

# WooCommerce-Shop
python crawler.py --domain example.com --shop-type woocommerce --extract-content

# Ohne --shop-type: alle bekannten Policy-Pfade werden probiert
python crawler.py --domain example.com --extract-content

# Nur bestimmte Kategorien
python crawler.py --domain probiom.com --extract-content --categories products
python crawler.py --domain probiom.com --extract-content --categories products,policies

# Alles AUSSER Blogs
python crawler.py --domain probiom.com --extract-content --exclude blogs

# Alles ausser Blogs und Collections
python crawler.py --domain probiom.com --extract-content --exclude blogs,collections

# Mit URL-Limit
python crawler.py --domain probiom.com --extract-content --max-urls 100

# Eigenes Output-Verzeichnis
python crawler.py --domain probiom.com --output /pfad/zum/ordner
```

### Shop-Type: Wann brauche ich das?

Policy-Seiten (Impressum, Datenschutz, AGB) sind oft **nicht in der Sitemap**. Der Crawler prüft deshalb bekannte Pfade per HTTP. Verschiedene Shop-Systeme nutzen unterschiedliche Pfade:

| Shop-Type | Geprüfte Pfade | Wann nutzen |
|-----------|---------------|-------------|
| `shopify` | `/policies/privacy-policy`, `/policies/legal-notice`, `/policies/terms-of-service`, `/policies/refund-policy`, `/policies/shipping-policy` | Für Shopify-Shops (z.B. eure Kunden) |
| `woocommerce` | `/privacy-policy`, `/terms-and-conditions`, `/impressum`, `/agb`, `/widerrufsbelehrung`, `/refund_returns` | Für WordPress/WooCommerce-Shops |
| `generic` | `/impressum`, `/datenschutz`, `/agb`, `/privacy-policy`, `/privacy`, `/terms`, `/terms-of-service`, `/legal-notice`, `/legal`, `/widerruf`, `/refund-policy` | Für unbekannte/andere Shop-Systeme |
| *(ohne)* | Alle Pfade kombiniert | Wenn du den Shop-Typ nicht kennst |

**Empfehlung:** Wenn du weißt, dass es ein Shopify-Shop ist, nutze `--shop-type shopify` – das ist schneller und präziser.

## Output

JSON-Dateien werden nach `output/` geschrieben (→ Dropbox-Sync):
- `*_urls.json` bei jedem Crawl
- `*_content.json` zusätzlich bei `--extract-content`

### JSON-Struktur (Content)

Die compliance-relevanten Felder (Titel, Meta-Description, Headings) stehen **vor** dem Fließtext, damit Clara sie priorisiert:

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

## Verfügbare Kategorien

`products`, `blogs`, `pages`, `collections`, `policies`, `other`

> **Hinweis:** `policies` wird automatisch entdeckt – die meisten Shop-Systeme haben Policy-Seiten nicht in der Sitemap.

## Hinweise

- Homepage wird IMMER mitgecrawlt (auch bei Filtern)
- 0.5s Pause zwischen Requests (Rate-Limiting)
- Timeout: 10s für Sitemaps, 15s für Content
- `--categories` und `--exclude` können nicht gleichzeitig verwendet werden
- `--max-urls`, `--categories` und `--exclude` erfordern `--extract-content`

## Entwicklung

```bash
# Tests
source venv/bin/activate && pytest -q

# Linting
source venv/bin/activate && ruff check crawler.py src/ tests/
```

Entwickelt mit Claude Code für Water & Salt AG.

## Lizenz

Privat - Manuel Hendel
