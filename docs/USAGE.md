# Usage Guide

## Grundlegende Nutzung

### Single Domain Scan
```bash
python src/crawler.py --domain probiom.com
```

### Mit spezifischem Compliance-Framework
```bash
python src/crawler.py --domain probiom.com --framework eu_health_claims
```

### Output-Format wählen
```bash
python src/crawler.py --domain probiom.com --format json
python src/crawler.py --domain probiom.com --format excel
```

## Erweiterte Optionen

### Verschiedene Sprachen ausschließen
```bash
python src/crawler.py --domain probiom.com --exclude-language /en/
```

### Maximale Seitenanzahl limitieren
```bash
python src/crawler.py --domain probiom.com --max-pages 50
```

### Verbose Logging
```bash
python src/crawler.py --domain probiom.com --verbose
```

## Output-Struktur

Alle Scans werden nach `output/` geschrieben (→ Dropbox):
```
output/
└── probiom.com_2025-11-17_15-30/
    ├── urls.json              # Alle gefundenen URLs
    ├── compliance_report.json # Gefundene Verstöße
    ├── compliance_report.xlsx # Excel-Report
    └── summary.txt            # Zusammenfassung
```

## Beispiel-Workflow

1. **Scan durchführen:**
```bash
   python src/crawler.py --domain probiom.com --framework eu_health_claims
```

2. **Reports in Dropbox finden:**
   - Öffne `~/Water&Salt Dropbox/.../Website-Crawler-Output/`
   - Neuester Ordner enthält die Results

3. **In Claude Projects hochladen:**
   - Upload `compliance_report.json`
   - Sag: "Clara, analysiere diesen Report"

## Clara & Mara Integration

Dieser Crawler ist der **Daten-Sammler** für Clara & Mara in Claude Projects:

- **Workflow:**
  1. Crawler sammelt URLs + Content
  2. Du uploadest Reports → Claude Projects
  3. Clara/Mara analysieren Compliance/Marketing

- **Warum getrennt?**
  - Clara/Mara existieren nur in Claude Projects (mit Memory)
  - Crawler braucht lokale Netzwerk-Rechte
  - Best of both worlds: Lokales Crawling + Cloud-Analyse
