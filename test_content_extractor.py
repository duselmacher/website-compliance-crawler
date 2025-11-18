#!/usr/bin/env python3
"""
Quick test for content extractor.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from content_extractor import extract_content

# Test mit einer probiom.com Produkt-URL
test_url = 'https://probiom.com/products/probiom-dental-1er-pack'

print(f"🧪 Testing Content Extractor mit: {test_url}\n")
print("⏳ Extracting content...\n")

result = extract_content(test_url)

# Zeige Ergebnisse
print("=" * 80)
print("📄 CONTENT EXTRACTION RESULTS")
print("=" * 80)
print(f"\nURL: {result['url']}")
print(f"Title: {result['title']}")
print(f"Meta Description: {result['meta_description'][:100]}..." if len(result['meta_description']) > 100 else f"Meta Description: {result['meta_description']}")
print(f"\nHeadings:")
print(f"  H1: {len(result['headings']['h1'])} found")
if result['headings']['h1']:
    for h1 in result['headings']['h1'][:3]:
        print(f"    - {h1}")
print(f"  H2: {len(result['headings']['h2'])} found")
if result['headings']['h2']:
    for h2 in result['headings']['h2'][:3]:
        print(f"    - {h2}")
print(f"  H3: {len(result['headings']['h3'])} found")

print(f"\nMain Content: {len(result['main_content'])} characters")
print(f"First 200 chars: {result['main_content'][:200]}...")

print(f"\nCTA Buttons: {len(result['cta_buttons'])} found")
for cta in result['cta_buttons'][:5]:
    print(f"  - {cta}")

print(f"\nProduct Info:")
print(f"  Name: {result['product_info']['name']}")
print(f"  Price: {result['product_info']['price']}")
print(f"  Description: {result['product_info']['description'][:100]}..." if len(result['product_info']['description']) > 100 else f"  Description: {result['product_info']['description']}")

if result['error']:
    print(f"\n⚠️  Error: {result['error']}")
else:
    print(f"\n✅ Extraction successful!")

print("=" * 80)

# Save as JSON
output_file = Path('output') / 'test_content_extraction.json'
output_file.parent.mkdir(exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n💾 Saved to: {output_file}")
