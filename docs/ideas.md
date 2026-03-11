# Ideen

## Prio
- **Lokales Web-Interface:** Statt CLI-Flags eine einfache UI zum Starten und Konfigurieren von Crawls (siehe unten)
- **Retry-Logik:** Bei fehlgeschlagenen HTTP-Requests automatisch 1-2x wiederholen
- **Fortschrittsanzeige:** Bei Content-Extraktion Prozent/Anzahl anzeigen statt nur Endstatistik

## Später
- **Diff-Modus:** Nur geänderte Seiten seit letztem Crawl extrahieren (spart Zeit bei Re-Crawls)
- **Clara-Integration:** Output direkt als Claude Projects Knowledge Base hochladen (API?)
- **HTML-Report:** Zusätzlich zum JSON einen lesbaren HTML-Report generieren
- **Parallelisierung:** Async HTTP-Requests für schnellere Content-Extraktion

## Web-Interface – Optionen

### Option A: Lokale Web-App (Flask/FastAPI + HTML)
- `python app.py` → Browser öffnet sich auf localhost:8000
- Formular: Domain eingeben, Shop-Type wählen, Kategorien an/abwählen, Start-Button
- Live-Fortschritt im Browser (SSE oder WebSocket)
- Ergebnisse direkt anzeigen + Download-Link
- **Pro:** Voll flexibel, Live-Feedback, könnte auch Crawl-Historie anzeigen
- **Contra:** Mehr Code, braucht Flask/FastAPI als Dependency

### Option B: TUI (Textual/Rich im Terminal)
- `python crawler.py` ohne Args → interaktives Terminal-Interface
- Felder zum Ausfüllen, Checkboxen für Kategorien, Fortschrittsbalken
- **Pro:** Keine Browser nötig, alles im Terminal, weniger Dependencies
- **Contra:** Weniger intuitiv als Web, Terminal-Fenster muss groß genug sein

### Option C: macOS-native (py2app oder rumps Menubar)
- Crawler als Menubar-App, Klick → kleines Fenster
- **Pro:** Fühlt sich wie echte App an
- **Contra:** Nur macOS, deutlich mehr Aufwand, schwieriger zu maintainen

### Empfehlung
**Option A (Flask)** – passt am besten zum Use Case:
- Du willst "Ding starten und Fenster geht auf" → genau das
- Browser-UI ist universell und braucht kein Terminal-Wissen
- Kann später auch Crawl-Historie und Ergebnisvergleiche zeigen
- Flask ist minimal (eine Datei, ~50 Zeilen für den Start)
