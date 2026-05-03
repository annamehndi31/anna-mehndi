import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://pyariwalls.pk/collections/all/products.json"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape():
    all_products = []
    page = 1
    while True:
        url = f"{BASE_URL}?limit=250&page={page}"
        print(f"Scraping page {page}...")
        r = requests.get(url, headers=headers)
        data = r.json()
        products = data.get("products", [])
        if not products:
            break
        for p in products:
            title = p.get("title", "")
            # Only wall art / laser products
            keywords = ["calligraphy", "wall", "islamic", "laser", "frame", "art"]
            if any(k in title.lower() for k in keywords):
                image = p["images"][0]["src"] if p.get("images") else ""
                variant = p["variants"][0] if p.get("variants") else {}
                price = float(variant.get("price", "0"))
                all_products.append({
                    "title": title,
                    "price": f"Rs. {price:.0f}",
                    "handle": p.get("handle", ""),
                    "link": f"https://pyariwalls.pk/products/{p.get('handle','')}",
                    "vendor": "Anna Mehndi Stencils",
                    "image": image,
                    "local_image": image,
                    "category": "Wall Art & CO2 Laser"
                })
        print(f"Found {len(products)} products on page {page}")
        page += 1
        time.sleep(1)
    return all_products

if __name__ == "__main__":
    products = scrape()
    print(f"\nTotal wall art: {len(products)}")
    with open("wall_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("Saved to wall_products.json!")
    for p in products[:3]:
        print(f"  - {p['title']} | {p['price']}")
