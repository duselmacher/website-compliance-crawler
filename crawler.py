#!/usr/bin/env -S venv/bin/python3
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
from urllib.parse import urlparse

# Add project root to path (for src.* imports when run directly via shebang)
sys.path.insert(0, str(Path(__file__).parent))

import requests

from src.content_extractor import extract_multiple_urls
from src.sitemap_parser import crawl_all_sitemaps

# Policy-Pfade nach Shop-System
POLICY_PATHS = {
    'shopify': [
        '/policies/legal-notice',
        '/policies/privacy-policy',
        '/policies/terms-of-service',
        '/policies/refund-policy',
        '/policies/shipping-policy',
    ],
    'woocommerce': [
        '/privacy-policy',
        '/terms-and-conditions',
        '/refund_returns',
        '/impressum',
        '/agb',
        '/widerrufsbelehrung',
    ],
    'generic': [
        '/impressum',
        '/datenschutz',
        '/agb',
        '/privacy-policy',
        '/privacy',
        '/terms',
        '/terms-of-service',
        '/legal-notice',
        '/legal',
        '/widerruf',
        '/refund-policy',
    ],
}

VALID_SHOP_TYPES = sorted(POLICY_PATHS.keys())


def get_policy_paths(shop_type: str = None) -> List[str]:
    """
    Gibt die Policy-Pfade für einen Shop-Typ zurück.

    Args:
        shop_type: Shop-Typ ('shopify', 'woocommerce', 'generic') oder None für alle

    Returns:
        Deduplizierte Liste von Policy-Pfaden
    """
    if shop_type:
        return POLICY_PATHS.get(shop_type, POLICY_PATHS['generic'])

    # Ohne Angabe: alle Pfade kombinieren (dedupliziert, Reihenfolge beibehalten)
    all_paths = []
    seen = set()
    for paths in POLICY_PATHS.values():
        for path in paths:
            if path not in seen:
                seen.add(path)
                all_paths.append(path)
    return all_paths


def discover_policy_urls(domain: str, shop_type: str = None) -> List[str]:
    """
    Prüft Policy-URLs die oft nicht in der Sitemap sind.

    Args:
        domain: Die Domain zum Prüfen
        shop_type: Shop-Typ für gezielte Pfade (None = alle probieren)

    Returns:
        Liste von existierenden Policy-URLs
    """
    found_urls = []
    base_url = f"https://{domain}"
    paths = get_policy_paths(shop_type)

    for path in paths:
        url = f"{base_url}{path}"
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                found_urls.append(url)
        except requests.RequestException:
            pass  # URL existiert nicht oder Fehler

    return found_urls


def normalize_domain(domain: str) -> str:
    """Normalisiert Domain-Eingaben (mit/ohne Schema) zu einem Hostnamen."""
    raw = domain.strip()
    if not raw:
        raise ValueError("Domain darf nicht leer sein")

    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = parsed.netloc or parsed.path
    host = host.strip().strip("/").lower()

    if not host:
        raise ValueError(f"Ungültige Domain: {domain}")

    return host


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


def crawl_urls_only(domain: str, output_dir: Path, shop_type: str = None) -> Dict:
    """
    Crawlt nur die Sitemap und sammelt URLs.

    Args:
        domain: Die Domain zum Crawlen
        output_dir: Output-Verzeichnis
        shop_type: Shop-Typ für Policy-Discovery (None = alle probieren)

    Returns:
        Dictionary mit URL-Daten
    """
    print_header(f"CRAWLING SITEMAP: {domain}")

    print("⏳ Fetching sitemap...\n")
    urls_data = crawl_all_sitemaps(domain)
    urls_data['urls'].setdefault('policies', [])

    # Bestehende URLs global sammeln, um doppelte Policy-URLs zu vermeiden
    existing_urls = set()
    for category_urls in urls_data['urls'].values():
        existing_urls.update(category_urls)

    # Policy-URLs entdecken (oft nicht in Sitemap)
    print("\n🔍 Checking for policy pages...")
    policy_urls = discover_policy_urls(domain, shop_type)
    new_policy_urls = [url for url in policy_urls if url not in existing_urls]
    if new_policy_urls:
        urls_data['urls']['policies'].extend(new_policy_urls)
        urls_data['total_urls'] += len(new_policy_urls)
        print(f"   Found {len(new_policy_urls)} policy pages (not in sitemap)")
    else:
        print("   No standard policy pages found")

    print_stats(urls_data)

    # URL-Report immer speichern (auch ohne Content-Extraktion)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain_clean = clean_domain_for_filename(domain)
    urls_file = output_dir / f"{domain_clean}_{timestamp}_urls.json"
    urls_output = {
        **urls_data,
        'crawled_at': datetime.now().isoformat(),
    }
    save_json(urls_output, urls_file)
    print(f"\n💾 URL report saved to: {urls_file}")

    return urls_data


def crawl_with_content(domain: str, output_dir: Path, max_urls: int = None,
                       categories: List[str] = None, exclude: List[str] = None,
                       shop_type: str = None) -> tuple:
    """
    Crawlt Sitemap UND extrahiert Content von allen URLs.

    Args:
        domain: Die Domain zum Crawlen
        output_dir: Output-Verzeichnis
        max_urls: Maximale Anzahl URLs zum Extrahieren (None = alle)
        categories: Liste von Kategorien zum Filtern (None = alle) - inklusiv
        exclude: Liste von Kategorien zum Ausschließen (None = keine) - exklusiv
        shop_type: Shop-Typ für Policy-Discovery (None = alle probieren)

    Returns:
        Tuple von (urls_data, content_data)
    """
    # 1. Crawl URLs
    urls_data = crawl_urls_only(domain, output_dir, shop_type)

    # 2. ALWAYS include homepage first
    homepage_url = f"https://{domain}"
    all_urls = [homepage_url]
    print(f"\n✅ Including homepage: {homepage_url}")

    # 3. Sammle URLs basierend auf Kategorien
    if categories:
        # Nur ausgewählte Kategorien (inklusiv)
        print(f"\n🔍 Including categories: {', '.join(categories)}")
        for category in categories:
            if category in urls_data['urls']:
                urls = urls_data['urls'][category]
                all_urls.extend(urls)
                print(f"  ✅ {category}: {len(urls)} URLs")
            else:
                print(f"  ⚠️  Category '{category}' not found")
    elif exclude:
        # Alle AUSSER ausgewählte Kategorien (exklusiv)
        print(f"\n🔍 Excluding categories: {', '.join(exclude)}")
        for category, urls in urls_data['urls'].items():
            if category not in exclude:
                all_urls.extend(urls)
                print(f"  ✅ {category}: {len(urls)} URLs")
            else:
                print(f"  ❌ {category}: {len(urls)} URLs (excluded)")
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

    # Dedupliziere URLs bei gleichbleibender Reihenfolge
    unique_urls = []
    seen = set()
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    all_urls = unique_urls

    content_results = extract_multiple_urls(all_urls)

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

  # URLs + Content crawlen
  %(prog)s --domain probiom.com --extract-content

  # Nur Produkte crawlen
  %(prog)s --domain probiom.com --extract-content --categories products

  # Alles AUSSER Blogs crawlen
  %(prog)s --domain probiom.com --extract-content --exclude blogs

  # Shopify-Shop gezielt crawlen
  %(prog)s --domain probiom.com --shop-type shopify

  # WooCommerce-Shop
  %(prog)s --domain example.com --shop-type woocommerce

  # Mit URL-Limit
  %(prog)s --domain probiom.com --extract-content --max-urls 100
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
        help='Nur diese Kategorien crawlen (products,blogs,pages,collections,policies,other)'
    )

    parser.add_argument(
        '--exclude',
        type=str,
        help='Diese Kategorien AUSSCHLIESSEN (z.B. --exclude blogs)'
    )

    parser.add_argument(
        '--shop-type',
        type=str,
        choices=VALID_SHOP_TYPES,
        help=f'Shop-System für Policy-Discovery ({", ".join(VALID_SHOP_TYPES)}). '
             'Ohne Angabe werden alle bekannten Pfade probiert.'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output'),
        help='Output-Verzeichnis (Standard: ./output)'
    )

    args = parser.parse_args()

    try:
        domain = normalize_domain(args.domain)
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    # Validierung
    if args.max_urls and not args.extract_content:
        print("❌ --max-urls requires --extract-content")
        return 1

    if args.categories and not args.extract_content:
        print("❌ --categories requires --extract-content")
        return 1

    if args.exclude and not args.extract_content:
        print("❌ --exclude requires --extract-content")
        return 1

    if args.categories and args.exclude:
        print("❌ --categories und --exclude können nicht gleichzeitig verwendet werden")
        return 1

    valid_categories = {'products', 'blogs', 'pages', 'collections', 'policies', 'other'}

    # Parse categories (inklusiv)
    categories = None
    if args.categories:
        categories = [cat.strip() for cat in args.categories.split(',')]
        invalid = [cat for cat in categories if cat not in valid_categories]
        if invalid:
            print(f"❌ Invalid categories: {', '.join(invalid)}")
            print(f"   Valid: {', '.join(valid_categories)}")
            return 1

    # Parse exclude (exklusiv)
    exclude = None
    if args.exclude:
        exclude = [cat.strip() for cat in args.exclude.split(',')]
        invalid = [cat for cat in exclude if cat not in valid_categories]
        if invalid:
            print(f"❌ Invalid exclude categories: {', '.join(invalid)}")
            print(f"   Valid: {', '.join(valid_categories)}")
            return 1

    # Start
    print("\n🚀 Website Compliance Crawler")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        if args.extract_content:
            # Full Crawl mit Content
            crawl_with_content(domain, args.output, args.max_urls, categories,
                               exclude, args.shop_type)
        else:
            # Nur URLs
            crawl_urls_only(domain, args.output, args.shop_type)

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
