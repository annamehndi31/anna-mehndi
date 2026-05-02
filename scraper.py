import requests
import json
import time

BASE_URL = "https://www.snhenaa.pk/collections/henna-stencils/products.json"
headers = {"User-Agent": "Mozilla/5.0"}

def scrape():
    all_products = []
    page = 1
    while True:
        url = f"{BASE_URL}?limit=250&page={page}"
        print(f"Scraping page {page}...")
        r = requests.get(url, headers=headers)
        products = r.json().get("products", [])
        if not products:
            break
        for p in products:
            image = p["images"][0]["src"] if p.get("images") else ""
            variant = p["variants"][0] if p.get("variants") else {}
            price = variant.get("price", "0")
            all_products.append({
                "title": p.get("title", "N/A"),
                "price": f"Rs. {float(price):.0f}",
                "handle": p.get("handle", ""),
                "link": f"https://www.snhenaa.pk/products/{p.get('handle','')}",
                "vendor": p.get("vendor", ""),
                "image": image
            })
        print(f"Got {len(products)} products")
        page += 1
        time.sleep(1)
    return all_products

if __name__ == "__main__":
    products = scrape()
    print(f"Total: {len(products)} products")
    with open("henna_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("Saved!")
