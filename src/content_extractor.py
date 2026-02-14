"""
Content Extractor für Website Compliance Crawler.

Extrahiert strukturierte Inhalte von Webseiten für spätere Compliance-Analyse.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urljoin
import re


# Timeout für HTTP Requests (Sekunden)
REQUEST_TIMEOUT = 15

# User Agent für Requests
USER_AGENT = 'Mozilla/5.0 (compatible; ComplianceCrawler/1.0)'


def fetch_html(url: str) -> str:
    """
    Fetcht HTML-Content von einer URL.

    Args:
        url: Die URL zum Fetchen

    Returns:
        HTML-Content als String

    Raises:
        requests.RequestException: Bei Netzwerkfehlern
    """
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': USER_AGENT},
            allow_redirects=True
        )
        response.raise_for_status()
        return response.text

    except requests.Timeout:
        raise requests.RequestException(f"Timeout beim Laden von {url}")
    except requests.HTTPError as e:
        raise requests.RequestException(
            f"HTTP Fehler {e.response.status_code}: {url}"
        )
    except Exception as e:
        raise requests.RequestException(f"Fehler beim Laden von {url}: {str(e)}")


def clean_text(text: str) -> str:
    """
    Bereinigt Text von überflüssigen Whitespaces und Zeilenumbrüchen.

    Args:
        text: Der zu bereinigende Text

    Returns:
        Bereinigter Text
    """
    if not text:
        return ""

    # Entferne mehrfache Whitespaces
    text = re.sub(r'\s+', ' ', text)

    # Entferne führende/trailing Whitespaces
    text = text.strip()

    return text


def extract_headings(soup: BeautifulSoup) -> Dict[str, List[str]]:
    """
    Extrahiert alle Überschriften (h1-h3) aus dem HTML.

    Args:
        soup: BeautifulSoup Objekt

    Returns:
        Dictionary mit Listen von Überschriften pro Level
    """
    headings = {
        'h1': [],
        'h2': [],
        'h3': []
    }

    for level in ['h1', 'h2', 'h3']:
        elements = soup.find_all(level)
        for elem in elements:
            text = clean_text(elem.get_text())
            if text:
                headings[level].append(text)

    return headings


def extract_meta_description(soup: BeautifulSoup) -> str:
    """
    Extrahiert die Meta Description.

    Args:
        soup: BeautifulSoup Objekt

    Returns:
        Meta Description oder leerer String
    """
    # Versuche verschiedene Meta-Tags
    meta_tags = [
        soup.find('meta', {'name': 'description'}),
        soup.find('meta', {'property': 'og:description'}),
        soup.find('meta', {'name': 'twitter:description'})
    ]

    for meta in meta_tags:
        if meta and meta.get('content'):
            return clean_text(meta.get('content'))

    return ""


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extrahiert den Seitentitel.

    Priorisierung:
    1. <title> Tag
    2. Erste <h1> Überschrift
    3. og:title Meta Tag

    Args:
        soup: BeautifulSoup Objekt

    Returns:
        Seitentitel oder leerer String
    """
    # 1. <title> Tag
    title_tag = soup.find('title')
    if title_tag:
        title = clean_text(title_tag.get_text())
        if title:
            return title

    # 2. Erste <h1>
    h1 = soup.find('h1')
    if h1:
        title = clean_text(h1.get_text())
        if title:
            return title

    # 3. og:title
    og_title = soup.find('meta', {'property': 'og:title'})
    if og_title and og_title.get('content'):
        return clean_text(og_title.get('content'))

    return ""


def extract_full_text(soup: BeautifulSoup) -> str:
    """
    Extrahiert den kompletten sichtbaren Text der Seite.

    Entfernt nur nicht-sichtbare Elemente wie Scripts und Styles,
    aber behält den gesamten Textinhalt der Seite.

    Args:
        soup: BeautifulSoup Objekt

    Returns:
        Kompletter sichtbarer Text der Seite
    """
    # Erstelle eine Kopie um Original nicht zu verändern
    soup_copy = BeautifulSoup(str(soup), 'html.parser')

    # Entferne nur unsichtbare Elemente
    for tag in soup_copy(['script', 'style', 'noscript']):
        tag.decompose()

    # Hole kompletten Body-Text
    body = soup_copy.find('body')
    if body:
        return clean_text(body.get_text())

    # Fallback: Gesamter Text
    return clean_text(soup_copy.get_text())


def extract_images(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """
    Extrahiert alle Bilder mit ihren Attributen.

    Args:
        soup: BeautifulSoup Objekt
        base_url: Basis-URL für relative Links

    Returns:
        Liste von Dictionaries mit Bildinformationen:
        [
            {
                'src': 'absolute URL',
                'alt': 'alt text',
                'title': 'title attribute'
            },
            ...
        ]
    """
    images = []

    for img in soup.find_all('img'):
        src = img.get('src', '')

        # Überspringe Bilder ohne src
        if not src:
            continue

        # Konvertiere relative URLs zu absoluten
        if src and not src.startswith(('http://', 'https://', 'data:')):
            src = urljoin(base_url, src)

        image_data = {
            'src': src,
            'alt': clean_text(img.get('alt', '')),
            'title': clean_text(img.get('title', ''))
        }

        images.append(image_data)

    return images


def extract_product_info(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrahiert Produkt-spezifische Informationen (für E-Commerce Sites).

    Sucht nach Schema.org Product Markup und anderen E-Commerce Patterns.

    Args:
        soup: BeautifulSoup Objekt

    Returns:
        Dictionary mit Produktinformationen
    """
    product_info = {
        'name': '',
        'description': '',
        'price': ''
    }

    # Schema.org Product Markup
    product_schema = soup.find(attrs={'itemtype': re.compile(r'schema.org/Product', re.I)})

    if product_schema:
        # Product Name
        name = product_schema.find(attrs={'itemprop': 'name'})
        if name:
            product_info['name'] = clean_text(name.get_text())

        # Product Description
        description = product_schema.find(attrs={'itemprop': 'description'})
        if description:
            product_info['description'] = clean_text(description.get_text())

        # Price
        price = product_schema.find(attrs={'itemprop': 'price'})
        if price:
            product_info['price'] = clean_text(price.get_text())

    # Fallback: Meta Tags
    if not product_info['name']:
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            product_info['name'] = clean_text(og_title.get('content', ''))

    if not product_info['description']:
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            product_info['description'] = clean_text(og_desc.get('content', ''))

    return product_info


def extract_content(url: str) -> Dict:
    """
    Extrahiert alle relevanten Inhalte von einer URL.

    Dies ist die Hauptfunktion die alle anderen Extraktionsfunktionen orchestriert.

    Args:
        url: Die URL zum Analysieren

    Returns:
        Dictionary mit strukturierten Content-Daten:
        {
            'url': str,
            'title': str,
            'meta_description': str,
            'full_text': str,
            'headings': {
                'h1': List[str],
                'h2': List[str],
                'h3': List[str]
            },
            'images': List[Dict[str, str]],
            'product_info': Dict[str, str],
            'error': Optional[str]
        }

    Example:
        content = extract_content('https://example.com/product')
        print(content['title'])
        print(content['full_text'])
    """
    result = {
        'url': url,
        'title': '',
        'meta_description': '',
        'full_text': '',
        'headings': {'h1': [], 'h2': [], 'h3': []},
        'images': [],
        'product_info': {'name': '', 'description': '', 'price': ''},
        'error': None
    }

    try:
        # 1. HTML fetchen
        html = fetch_html(url)

        # 2. HTML parsen
        soup = BeautifulSoup(html, 'html.parser')

        # 3. Daten extrahieren
        result['title'] = extract_title(soup)
        result['meta_description'] = extract_meta_description(soup)
        result['full_text'] = extract_full_text(soup)
        result['headings'] = extract_headings(soup)
        result['images'] = extract_images(soup, url)
        result['product_info'] = extract_product_info(soup)

    except Exception as e:
        result['error'] = str(e)

    return result


def extract_multiple_urls(urls: List[str]) -> List[Dict]:
    """
    Extrahiert Content von mehreren URLs.

    Args:
        urls: Liste von URLs

    Returns:
        Liste von Content-Dictionaries

    Example:
        urls = ['https://example.com/page1', 'https://example.com/page2']
        results = extract_multiple_urls(urls)
        for result in results:
            print(f"{result['url']}: {result['title']}")
    """
    results = []

    for url in urls:
        print(f"Extracting: {url}")
        content = extract_content(url)
        results.append(content)

        # Kleine Pause um Server nicht zu überlasten
        import time
        time.sleep(0.5)

    return results
