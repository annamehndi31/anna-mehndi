#!/bin/bash
echo "Setting up Anna Mehndi Stencils shop..."

# Create folders
mkdir -p static/css static/js static/images/products templates

# Create scraper
cat > scraper.py << 'PYEOF'
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
PYEOF

# Create image downloader
cat > download_images.py << 'PYEOF'
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
PYEOF

# Create app.py
cat > app.py << 'PYEOF'
from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = "annahenna2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(500))
    link = db.Column(db.String(500))
    vendor = db.Column(db.String(100))

@app.route("/")
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/add-to-cart/<int:id>")
def add_to_cart(id):
    cart = session.get("cart", {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    session["cart"] = cart
    return redirect(url_for("index"))

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []
    total = 0
    for pid, qty in cart.items():
        p = Product.query.get(int(pid))
        if p:
            subtotal = p.price * qty
            items.append({"product": p, "qty": qty, "subtotal": subtotal})
            total += subtotal
    return render_template("cart.html", items=items, total=total)

@app.route("/remove/<int:id>")
def remove(id):
    cart = session.get("cart", {})
    cart.pop(str(id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            with open("henna_products.json") as f:
                products = json.load(f)
            for p in products:
                try:
                    price = float(p["price"].replace("Rs.", "").strip())
                except:
                    price = 0
                db.session.add(Product(
                    title=p["title"],
                    price=price,
                    image=p.get("local_image", ""),
                    link=p["link"],
                    vendor=p["vendor"]
                ))
            db.session.commit()
            print(f"Imported {len(products)} products!")
    app.run(debug=True)
PYEOF

# Create index.html
cat > templates/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anna Mehndi Stencils</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; }
        header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        header h1 { font-size: 1.5rem; }
        nav a { color: white; text-decoration: none; margin-left: 1.5rem; }
        .hero { background: linear-gradient(135deg, #1a1a2e, #e94560); color: white; text-align: center; padding: 3rem; }
        .hero h2 { font-size: 2rem; margin-bottom: 0.5rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .card img { width: 100%; height: 200px; object-fit: cover; }
        .no-img { width: 100%; height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 3rem; }
        .card-body { padding: 1rem; }
        .card-body h3 { font-size: 0.9rem; margin-bottom: 0.5rem; height: 2.5rem; overflow: hidden; }
        .price { color: #e94560; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
        .btn { display: block; background: #e94560; color: white; text-align: center; padding: 0.5rem; border-radius: 6px; text-decoration: none; }
        .btn:hover { background: #c73652; }
        footer { background: #1a1a2e; color: white; text-align: center; padding: 1.5rem; margin-top: 2rem; }
    </style>
</head>
<body>
    <header>
        <h1>🌿 Anna Mehndi Stencils</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/cart">🛒 Cart</a>
        </nav>
    </header>
    <div class="hero">
        <h2>Anna Mehndi Stencils</h2>
        <p>Premium quality henna stencils 🌿</p>
    </div>
    <div class="grid">
        {% for p in products %}
        <div class="card">
            {% if p.image %}
            <img src="{{ url_for('static', filename='images/products/' + p.image) }}" alt="{{ p.title }}">
            {% else %}
            <div class="no-img">🌿</div>
            {% endif %}
            <div class="card-body">
                <h3>{{ p.title }}</h3>
                <p class="price">Rs. {{ p.price|int }}</p>
                <a href="/add-to-cart/{{ p.id }}" class="btn">Add to Cart</a>
            </div>
        </div>
        {% endfor %}
    </div>
    <footer><p>© 2024 Anna Mehndi Stencils</p></footer>
</body>
</html>
HTMLEOF

# Create cart.html
cat > templates/cart.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cart - Anna Mehndi Stencils</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; }
        header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; }
        header a { color: white; text-decoration: none; margin-left: 1rem; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        h2 { margin-bottom: 1.5rem; }
        .item { background: white; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .total { text-align: right; font-size: 1.3rem; font-weight: bold; margin-top: 1rem; color: #e94560; }
        .remove { color: red; text-decoration: none; font-size: 0.85rem; }
        .empty { text-align: center; padding: 3rem; color: #666; }
        .back { display: inline-block; background: #1a1a2e; color: white; padding: 0.6rem 1.2rem; border-radius: 6px; text-decoration: none; margin-top: 1rem; }
    </style>
</head>
<body>
    <header>
        <h1>🛒 Cart</h1>
        <nav><a href="/">← Back to Shop</a></nav>
    </header>
    <div class="container">
        <h2>Your Cart</h2>
        {% if items %}
            {% for item in items %}
            <div class="item">
                <div>
                    <strong>{{ item.product.title }}</strong><br>
                    <small>Rs. {{ item.product.price|int }} × {{ item.qty }}</small>
                </div>
                <div>
                    <strong>Rs. {{ item.subtotal|int }}</strong><br>
                    <a href="/remove/{{ item.product.id }}" class="remove">Remove</a>
                </div>
            </div>
            {% endfor %}
            <div class="total">Total: Rs. {{ total|int }}</div>
        {% else %}
            <div class="empty">
                <p>Cart is empty 😢</p>
                <a href="/" class="back">Go Shopping</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
HTMLEOF

echo "All files created!"
echo "Now running scraper..."
python3 scraper.py
echo "Downloading images..."
python3 download_images.py
echo "Launching shop..."
python3 app.py
