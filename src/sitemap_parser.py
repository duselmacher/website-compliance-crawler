"""
Sitemap Parser für generisches Website Crawling.

Dieses Modul lädt und parst XML-Sitemaps von beliebigen Domains.
Unterstützt:
- Standard Sitemaps
- Sitemap Index Files (Parent Sitemaps)
- Rekursives Crawling aller Kind-Sitemaps
- URL-Kategorisierung nach Pfad-Typ
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
import time


# XML Namespaces für Sitemaps
SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

# Timeout für HTTP Requests (Sekunden)
REQUEST_TIMEOUT = 10

# User Agent für Requests
USER_AGENT = 'Mozilla/5.0 (compatible; ComplianceCrawler/1.0)'


def parse_sitemap(url: str) -> List[str]:
    """
    Parst eine einzelne Sitemap XML und extrahiert alle <loc> URLs.

    Args:
        url: Die URL zur Sitemap XML (z.B. https://example.com/sitemap.xml)

    Returns:
        Liste von URL-Strings aus der Sitemap

    Raises:
        requests.RequestException: Bei Netzwerkfehlern
        ET.ParseError: Bei ungültigem XML
    """
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': USER_AGENT}
        )
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Extrahiere alle <loc> Tags
        urls = []

        # Versuche mit Namespace
        for url_elem in root.findall('.//sm:loc', SITEMAP_NS):
            if url_elem.text:
                urls.append(url_elem.text.strip())

        # Fallback: Versuche ohne Namespace (manche Sitemaps nutzen keinen)
        if not urls:
            for url_elem in root.findall('.//loc'):
                if url_elem.text:
                    urls.append(url_elem.text.strip())

        return urls

    except requests.Timeout:
        raise requests.RequestException(f"Timeout beim Laden von {url}")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise requests.RequestException(f"Sitemap nicht gefunden: {url} (404)")
        raise requests.RequestException(f"HTTP Fehler {e.response.status_code}: {url}")
    except ET.ParseError as e:
        raise ET.ParseError(f"Ungültiges XML in {url}: {str(e)}")


def parse_sitemap_index(url: str) -> List[str]:
    """
    Parst eine Sitemap Index Datei und extrahiert alle Kind-Sitemap URLs.

    Eine Sitemap Index Datei enthält <sitemap> Tags mit <loc> zu anderen Sitemaps.

    Args:
        url: Die URL zum Sitemap Index (z.B. https://example.com/sitemap.xml)

    Returns:
        Liste von URLs zu Kind-Sitemaps

    Raises:
        requests.RequestException: Bei Netzwerkfehlern
        ET.ParseError: Bei ungültigem XML
    """
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': USER_AGENT}
        )
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Extrahiere alle <sitemap><loc> Tags (für Sitemap Index)
        sitemap_urls = []

        # Mit Namespace
        for sitemap_elem in root.findall('.//sm:sitemap/sm:loc', SITEMAP_NS):
            if sitemap_elem.text:
                sitemap_urls.append(sitemap_elem.text.strip())

        # Fallback ohne Namespace
        if not sitemap_urls:
            for sitemap_elem in root.findall('.//sitemap/loc'):
                if sitemap_elem.text:
                    sitemap_urls.append(sitemap_elem.text.strip())

        return sitemap_urls

    except requests.Timeout:
        raise requests.RequestException(f"Timeout beim Laden von {url}")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise requests.RequestException(f"Sitemap Index nicht gefunden: {url} (404)")
        raise requests.RequestException(f"HTTP Fehler {e.response.status_code}: {url}")
    except ET.ParseError as e:
        raise ET.ParseError(f"Ungültiges XML in {url}: {str(e)}")


def categorize_url(url: str) -> str:
    """
    Kategorisiert eine URL basierend auf ihrem Pfad.

    Args:
        url: Die zu kategorisierende URL

    Returns:
        Kategorie-String: 'products', 'blogs', 'pages', 'collections', oder 'other'
    """
    parsed = urlparse(url)
    path = parsed.path.lower()

    # Kategorisierung nach Pfad-Präfix
    if '/product' in path:
        return 'products'
    elif '/blog' in path or '/artikel' in path or '/news' in path:
        return 'blogs'
    elif '/collection' in path or '/kategorie' in path or '/category' in path:
        return 'collections'
    elif '/page' in path or '/seite' in path:
        return 'pages'
    else:
        return 'other'


def find_sitemap_url(domain: str) -> str:
    """
    Findet die Sitemap URL für eine gegebene Domain.

    Versucht verschiedene Standard-Locations:
    - https://domain/sitemap.xml
    - https://domain/sitemap_index.xml
    - http://domain/sitemap.xml (Fallback)

    Args:
        domain: Die Domain (z.B. 'example.com' oder 'https://example.com')

    Returns:
        Die gefundene Sitemap URL

    Raises:
        requests.RequestException: Wenn keine Sitemap gefunden wurde
    """
    # Stelle sicher, dass Domain ein Schema hat
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    # Entferne trailing slash
    domain = domain.rstrip('/')

    # Standard Sitemap Locations
    sitemap_paths = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap-index.xml',
    ]

    for path in sitemap_paths:
        sitemap_url = f"{domain}{path}"
        try:
            response = requests.head(
                sitemap_url,
                timeout=REQUEST_TIMEOUT,
                headers={'User-Agent': USER_AGENT},
                allow_redirects=True
            )
            if response.status_code == 200:
                return sitemap_url
        except requests.RequestException:
            continue

    # Fallback zu HTTP wenn HTTPS fehlschlägt
    if domain.startswith('https://'):
        http_domain = domain.replace('https://', 'http://')
        for path in sitemap_paths:
            sitemap_url = f"{http_domain}{path}"
            try:
                response = requests.head(
                    sitemap_url,
                    timeout=REQUEST_TIMEOUT,
                    headers={'User-Agent': USER_AGENT},
                    allow_redirects=True
                )
                if response.status_code == 200:
                    return sitemap_url
            except requests.RequestException:
                continue

    raise requests.RequestException(f"Keine Sitemap gefunden für {domain}")


def crawl_all_sitemaps(domain: str) -> Dict[str, any]:
    """
    Crawlt alle Sitemaps einer Domain und extrahiert alle URLs strukturiert.

    Diese Funktion:
    1. Findet die Haupt-Sitemap der Domain
    2. Erkennt ob es ein Sitemap Index ist
    3. Crawlt rekursiv alle Kind-Sitemaps
    4. Kategorisiert alle gefundenen URLs
    5. Gibt strukturierte Daten zurück

    Args:
        domain: Die Domain zum Crawlen (z.B. 'example.com')

    Returns:
        Dictionary mit:
        - 'domain': Die gecrawlte Domain
        - 'sitemap_url': Die Haupt-Sitemap URL
        - 'total_urls': Gesamtzahl gefundener URLs
        - 'urls': Dictionary mit URLs nach Kategorie
        - 'errors': Liste von Fehlern während des Crawlings

    Example:
        {
            'domain': 'example.com',
            'sitemap_url': 'https://example.com/sitemap.xml',
            'total_urls': 150,
            'urls': {
                'products': ['https://example.com/product/1', ...],
                'blogs': ['https://example.com/blog/post-1', ...],
                'pages': ['https://example.com/about', ...],
                'collections': [...],
                'other': [...]
            },
            'errors': []
        }
    """
    result = {
        'domain': domain,
        'sitemap_url': None,
        'total_urls': 0,
        'urls': {
            'products': [],
            'blogs': [],
            'pages': [],
            'collections': [],
            'other': []
        },
        'errors': []
    }

    try:
        # 1. Finde Sitemap URL
        sitemap_url = find_sitemap_url(domain)
        result['sitemap_url'] = sitemap_url

        # 2. Versuche zuerst als Sitemap Index zu parsen
        all_urls: Set[str] = set()
        sitemap_urls_to_process = [sitemap_url]
        processed_sitemaps: Set[str] = set()

        while sitemap_urls_to_process:
            current_sitemap = sitemap_urls_to_process.pop(0)

            # Vermeide doppeltes Processing
            if current_sitemap in processed_sitemaps:
                continue
            processed_sitemaps.add(current_sitemap)

            try:
                # Versuche als Sitemap Index (Parent Sitemap)
                child_sitemaps = parse_sitemap_index(current_sitemap)

                if child_sitemaps:
                    # Es ist ein Index - füge Kind-Sitemaps zur Queue hinzu
                    sitemap_urls_to_process.extend(child_sitemaps)
                else:
                    # Keine Kind-Sitemaps gefunden - versuche als normale Sitemap
                    urls = parse_sitemap(current_sitemap)
                    all_urls.update(urls)

            except Exception as e:
                # Wenn Sitemap Index fehlschlägt, versuche als normale Sitemap
                try:
                    urls = parse_sitemap(current_sitemap)
                    all_urls.update(urls)
                except Exception as parse_error:
                    result['errors'].append({
                        'sitemap': current_sitemap,
                        'error': str(parse_error)
                    })

            # Kleine Pause um Server nicht zu überlasten
            time.sleep(0.5)

        # 3. Kategorisiere alle URLs
        for url in all_urls:
            category = categorize_url(url)
            result['urls'][category].append(url)

        # 4. Zähle total
        result['total_urls'] = len(all_urls)

    except Exception as e:
        result['errors'].append({
            'sitemap': 'main',
            'error': str(e)
        })

    return result
