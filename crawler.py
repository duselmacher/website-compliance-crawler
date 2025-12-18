#!/usr/bin/env python3
"""
Website Compliance Crawler - CLI Tool

Crawlt Websites und extrahiert strukturierte Daten für Compliance-Analyse.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sitemap_parser import crawl_all_sitemaps
from content_extractor import extract_multiple_urls


def clean_domain_for_filename(domain: str) -> str:
    """Bereinigt Domain für Dateinamen."""
    return domain.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')


def save_json(data: Dict, filepath: Path) -> None:
    """Speichert Daten als JSON."""
    filepath.parent.mkdir(exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_header(text: str) -> None:
    """Druckt formatierten Header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_stats(urls_data: Dict) -> None:
    """Druckt Statistiken über gefundene URLs."""
    print(f"Domain:       {urls_data['domain']}")
    print(f"Sitemap URL:  {urls_data['sitemap_url']}")
    print(f"Total URLs:   {urls_data['total_urls']}")
    print("\nURLs by Category:")
    for category, urls in urls_data['urls'].items():
        count = len(urls)
        if count > 0:
            print(f"  {category:12s}: {count:4d} URLs")

    if urls_data['errors']:
        print(f"\nErrors: {len(urls_data['errors'])}")


def crawl_urls_only(domain: str, output_dir: Path) -> Dict:
    """
    Crawlt nur die Sitemap und sammelt URLs.

    Args:
        domain: Die Domain zum Crawlen
        output_dir: Output-Verzeichnis

    Returns:
        Dictionary mit URL-Daten
    """
    print_header(f"CRAWLING SITEMAP: {domain}")

    print("⏳ Fetching sitemap...\n")
    urls_data = crawl_all_sitemaps(domain)

    print_stats(urls_data)

    return urls_data


def crawl_with_content(domain: str, output_dir: Path, max_urls: int = None, categories: List[str] = None) -> tuple:
    """
    Crawlt Sitemap UND extrahiert Content von allen URLs.

    Args:
        domain: Die Domain zum Crawlen
        output_dir: Output-Verzeichnis
        max_urls: Maximale Anzahl URLs zum Extrahieren (None = alle)
        categories: Liste von Kategorien zum Filtern (None = alle)

    Returns:
        Tuple von (urls_data, content_data)
    """
    # 1. Crawl URLs
    urls_data = crawl_urls_only(domain, output_dir)

    # 2. ALWAYS include homepage first
    homepage_url = f"https://{domain}"
    all_urls = [homepage_url]
    print(f"\n✅ Including homepage: {homepage_url}")

    # 3. Sammle URLs basierend auf Kategorien
    if categories:
        # Nur ausgewählte Kategorien
        print(f"\n🔍 Filtering categories: {', '.join(categories)}")
        for category in categories:
            if category in urls_data['urls']:
                urls = urls_data['urls'][category]
                all_urls.extend(urls)
                print(f"  {category}: {len(urls)} URLs")
            else:
                print(f"  ⚠️  Category '{category}' not found")
    else:
        # Alle Kategorien
        for category, urls in urls_data['urls'].items():
            all_urls.extend(urls)

    # Limitiere URLs wenn gewünscht (aber behalte immer die Homepage)
    if max_urls and len(all_urls) > max_urls:
        print(f"\n⚠️  Limiting to first {max_urls} URLs (total: {len(all_urls)})")
        # Keep homepage (first URL) and limit the rest
        all_urls = [all_urls[0]] + all_urls[1:max_urls]

    # Show final statistics
    filtered_count = len(all_urls) - 1  # Minus homepage
    print(f"\n📊 Total to crawl: {len(all_urls)} URLs (1 homepage + {filtered_count} filtered)")

    # 4. Extrahiere Content
    print_header(f"EXTRACTING CONTENT: {len(all_urls)} URLs")

    content_results = []
    total = len(all_urls)

    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{total}] Extracting: {url}")

        # Import hier um Fortschritt zu zeigen
        from content_extractor import extract_content
        content = extract_content(url)
        content_results.append(content)

        # Kleine Pause
        import time
        time.sleep(0.5)

    # 4. Statistiken
    successful = sum(1 for r in content_results if not r['error'])
    failed = sum(1 for r in content_results if r['error'])

    print(f"\n✅ Successful: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")

    # 5. Save Content
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain_clean = clean_domain_for_filename(domain)
    content_file = output_dir / f"{domain_clean}_{timestamp}_content.json"

    content_data = {
        'domain': domain,
        'crawled_at': datetime.now().isoformat(),
        'total_urls': len(content_results),
        'successful': successful,
        'failed': failed,
        'content': content_results
    }

    save_json(content_data, content_file)
    print(f"\n💾 Content saved to: {content_file}")

    return urls_data, content_data


def main():
    """Hauptfunktion - CLI Entry Point."""
    parser = argparse.ArgumentParser(
        description='Website Compliance Crawler - Crawlt Websites für Compliance-Analyse',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Nur URLs crawlen (schnell)
  %(prog)s --domain probiom.com

  # URLs + Content crawlen (langsam, für Compliance-Analyse)
  %(prog)s --domain probiom.com --extract-content

  # Nur Produkte mit Content extrahieren
  %(prog)s --domain probiom.com --extract-content --categories products

  # Mehrere Kategorien
  %(prog)s --domain probiom.com --extract-content --categories products,pages

  # Nur erste 50 Blog-Posts
  %(prog)s --domain probiom.com --extract-content --categories blogs --max-urls 50
        """
    )

    parser.add_argument(
        '--domain',
        required=True,
        help='Domain zum Crawlen (z.B. probiom.com)'
    )

    parser.add_argument(
        '--extract-content',
        action='store_true',
        help='Extrahiert auch Content von allen URLs (langsam!)'
    )

    parser.add_argument(
        '--max-urls',
        type=int,
        help='Maximale Anzahl URLs für Content-Extraktion (Standard: alle)'
    )

    parser.add_argument(
        '--categories',
        type=str,
        help='Komma-separierte Liste von Kategorien (products,blogs,pages,collections,other)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output'),
        help='Output-Verzeichnis (Standard: ./output)'
    )

    args = parser.parse_args()

    # Validierung
    if args.max_urls and not args.extract_content:
        print("❌ --max-urls requires --extract-content")
        return 1

    if args.categories and not args.extract_content:
        print("❌ --categories requires --extract-content")
        return 1

    # Parse categories
    categories = None
    if args.categories:
        categories = [cat.strip() for cat in args.categories.split(',')]
        valid_categories = {'products', 'blogs', 'pages', 'collections', 'other'}
        invalid = [cat for cat in categories if cat not in valid_categories]
        if invalid:
            print(f"❌ Invalid categories: {', '.join(invalid)}")
            print(f"   Valid: {', '.join(valid_categories)}")
            return 1

    # Start
    print("\n🚀 Website Compliance Crawler")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        if args.extract_content:
            # Full Crawl mit Content
            crawl_with_content(args.domain, args.output, args.max_urls, categories)
        else:
            # Nur URLs
            crawl_urls_only(args.domain, args.output)

        print_header("✅ CRAWLING COMPLETED")
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Aborted by user")
        return 130

    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
