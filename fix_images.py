import json

with open('henna_products.json', encoding='utf-8') as f:
    products = json.load(f)

for p in products:
    p['local_image'] = p['image']

with open('henna_products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f"Fixed {len(products)} products with CDN images!")
