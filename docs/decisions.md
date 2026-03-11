# Architekturentscheidungen

## 2025-11-17 – Projekt-Setup als lokales CLI-Tool
- **Entscheidung:** Einfaches Python-Script statt Web-App oder Package
- **Grund:** Tool wird nur lokal genutzt, kein Deployment nötig. Shebang-Line erlaubt direktes Ausführen.
- **Konsequenz:** Kein pyproject.toml, kein Package-Management, einfacher `sys.path.insert` für src/

## 2025-11-17 – Output via Dropbox-Symlink
- **Entscheidung:** `output/` als Symlink zu Dropbox statt Upload-Mechanismus
- **Grund:** Einfachste Lösung um JSON-Dateien zu Clara (Claude Projects) zu transportieren
- **Konsequenz:** Nur auf Manuels Rechner mit korrekt konfiguriertem Symlink nutzbar

## 2025-12-19 – Auto-Discovery von Policy-URLs
- **Entscheidung:** Standard-Shopify-Policy-Pfade automatisch prüfen
- **Grund:** Impressum, Datenschutz, AGB etc. sind bei Shopify oft nicht in der Sitemap
- **Konsequenz:** Zusätzliche HTTP-HEAD-Requests pro Domain, aber compliance-relevante Seiten werden gefunden

## 2026-03-11 – Projekt-Init mit docs/-Struktur
- **Entscheidung:** Einführung von decisions.md, todo.md, ideas.md, changelog.md, sessions/
- **Grund:** Langzeit-Dokumentation für Claude Code Sessions gemäß globalem Workflow

## 2026-03-11 – JSON-Feld-Reihenfolge: Compliance-Signale zuerst
- **Entscheidung:** headings und meta_description kommen im JSON vor full_text
- **Grund:** Clara (und Behörden/Google) prüfen Überschriften und Meta-Descriptions auf Health Claims – diese Felder sollen nicht im Fließtext untergehen

## 2026-03-11 – ruff statt black/pylint/mypy
- **Entscheidung:** ruff als einzigen Linter verwenden
- **Grund:** Schneller, einfacher, ersetzt black+pylint+isort in einem Tool. Für ein lokales CLI-Tool reicht das

## 2026-03-11 – Policy-Pfade: Dict statt Auto-Detection
- **Entscheidung:** Policy-Pfade als Dict nach Shop-Typ (shopify, woocommerce, generic) statt automatischer Shop-Erkennung
- **Grund:** Auto-Detection (Meta-Tags, Signaturen) wäre komplex und fehleranfällig. `--shop-type` CLI-Flag ist einfacher und explizit. Ohne Angabe werden alle Pfade probiert.
- **Konsequenz:** Neue Shop-Systeme nur durch Ergänzung des POLICY_PATHS Dicts hinzufügbar
