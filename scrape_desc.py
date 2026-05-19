import requests
from bs4 import BeautifulSoup
import json
import time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get_product_description(handle):
    url = f"https://pyariwalls.pk/products/{handle}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try different description selectors
        desc = (
            soup.select_one('.product__description') or
            soup.select_one('.product-description') or
            soup.select_one('[class*="description"]') or
            soup.select_one('.rte')
        )
        
        if desc:
            return desc.get_text(strip=True, separator=' ')
        return ""
    except Exception as e:
        print(f"Error {handle}: {e}")
        return ""

# Load products
with open('henna_products.json', encoding='utf-8') as f:
    products = json.load(f)

# Only wall art products
wall_products = [p for p in products if p.get('category') == 'Wall Art & CO2 Laser']
print(f"Found {len(wall_products)} wall art products")

for i, p in enumerate(wall_products):
    handle = p.get('handle', '')
    if handle:
        desc = get_product_description(handle)
        p['description'] = desc
        print(f"{i+1}/{len(wall_products)} - {p['title'][:30]} - {len(desc)} chars")
        time.sleep(1)

# Save back
with open('henna_products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("Done!")
