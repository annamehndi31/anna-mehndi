import json, requests, os, time

with open("henna_products.json") as f:
    products = json.load(f)

os.makedirs("static/images/products", exist_ok=True)

for i, p in enumerate(products):
    if p.get("image"):
        try:
            img_data = requests.get(p["image"]).content
            filename = f"product_{i+1}.jpg"
            with open(f"static/images/products/{filename}", "wb") as f:
                f.write(img_data)
            p["local_image"] = filename
            print(f"✓ {i+1}/{len(products)}")
            time.sleep(0.2)
        except Exception as e:
            print(f"✗ {i+1} failed: {e}")

with open("henna_products.json", "w") as f:
    json.dump(products, f, indent=2)
print("Images done!")
