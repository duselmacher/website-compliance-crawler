# Setup Guide

## Voraussetzungen
- Python 3.8+
- Git
- Zugriff auf Dropbox (für Output-Sync)

## Installation

### 1. Repository klonen / navigieren
```bash
cd ~/Development/tools/website-compliance-crawler
```

### 2. Virtual Environment erstellen (empfohlen)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

## Projekt-Struktur
```
website-compliance-crawler/
├── .git/                  # Git Repository
├── .gitignore            # Git Ignore Rules
├── README.md             # Projekt-Übersicht
├── requirements.txt      # Python Dependencies
├── src/                  # Source Code
├── config/               # Konfigurationsdateien
│   └── *.yaml           # Compliance-Regeln pro Framework
├── tests/                # Unit Tests
├── docs/                 # Dokumentation
└── output/               # Symlink → Dropbox (nicht in Git!)
```

## Output-Ordner (Symlink)
Der `output/` Ordner ist ein **Symlink** nach Dropbox:
- **Ziel:** `~/Water&Salt Dropbox/Manuel Hendel/2_Area/Water & Salt AG/Compliance/Website-Crawler-Output`
- **Zweck:** Crawler-Reports werden automatisch in Dropbox gesichert
- **Git:** Wird via `.gitignore` ausgeschlossen

## Troubleshooting
- Falls Symlink kaputt: `ln -s "~/Water&Salt Dropbox/Manuel Hendel/2_Area/Water & Salt AG/Compliance/Website-Crawler-Output" output`
