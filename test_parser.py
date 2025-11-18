#!/usr/bin/env python3
"""
Test Script für Sitemap Parser.

Crawlt probiom.com und zeigt die Ergebnisse an.
Speichert das Ergebnis als JSON im output/ Ordner.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Füge src/ zum Python Path hinzu
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sitemap_parser import crawl_all_sitemaps


def format_results(result: dict) -> str:
    """Formatiert die Ergebnisse für die Konsolen-Ausgabe."""
    lines = []
    lines.append("=" * 80)
    lines.append(f"🌐 SITEMAP CRAWLING RESULTS")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Domain:       {result['domain']}")
    lines.append(f"Sitemap URL:  {result['sitemap_url']}")
    lines.append(f"Total URLs:   {result['total_urls']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("📊 URLs by Category:")
    lines.append("-" * 80)

    for category, urls in result['urls'].items():
        count = len(urls)
        if count > 0:
            lines.append(f"\n{category.upper()}: {count} URLs")
            # Zeige erste 5 URLs als Beispiel
            for i, url in enumerate(urls[:5], 1):
                lines.append(f"  {i}. {url}")
            if count > 5:
                lines.append(f"  ... und {count - 5} weitere")

    # Fehler
    if result['errors']:
        lines.append("")
        lines.append("-" * 80)
        lines.append("⚠️  ERRORS:")
        lines.append("-" * 80)
        for error in result['errors']:
            lines.append(f"  • {error['sitemap']}: {error['error']}")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def save_json(result: dict, domain: str) -> Path:
    """Speichert das Ergebnis als JSON im output/ Ordner."""
    # Erstelle output/ Ordner falls nicht vorhanden
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)

    # Dateiname mit Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain_clean = domain.replace('https://', '').replace('http://', '').replace('/', '_')
    filename = f"{domain_clean}_{timestamp}.json"
    filepath = output_dir / filename

    # Speichern
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return filepath


def main():
    """Hauptfunktion - Crawlt probiom.com und zeigt Ergebnisse."""
    domain = 'probiom.com'

    print(f"\n🚀 Starte Sitemap Crawling für: {domain}")
    print(f"⏳ Bitte warten...\n")

    try:
        # Crawl durchführen
        result = crawl_all_sitemaps(domain)

        # Ergebnisse anzeigen
        print(format_results(result))

        # Als JSON speichern
        filepath = save_json(result, domain)
        print(f"💾 Ergebnisse gespeichert: {filepath}")
        print("")

        # Exit Code basierend auf Erfolg
        if result['errors']:
            print("⚠️  Crawling mit Fehlern abgeschlossen")
            return 1
        else:
            print("✅ Crawling erfolgreich abgeschlossen")
            return 0

    except Exception as e:
        print(f"❌ FEHLER: {str(e)}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
