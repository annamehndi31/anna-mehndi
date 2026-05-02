from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
import json, os, urllib.parse

app = Flask(__name__)
app.secret_key = "annahenna2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(500))
    link = db.Column(db.String(500))
    vendor = db.Column(db.String(100))

with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        if os.path.exists("henna_products.json"):
            with open("henna_products.json", encoding="utf-8") as f:
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
                    vendor=p.get("vendor", "")
                ))
            db.session.commit()
            print(f"Imported {len(products)} products!")

@app.route("/")
def index():
    search = request.args.get("search", "")
    if search:
        products = Product.query.filter(Product.title.ilike(f"%{search}%")).all()
    else:
        products = Product.query.all()
    return render_template("index.html", products=products, search=search)

@app.route("/product/<int:id>")
def product(id):
    p = Product.query.get_or_404(id)
    return render_template("product.html", product=p)

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

@app.route("/checkout")
def checkout():
    cart = session.get("cart", {})
    msg = "Assalam o Alaikum! I want to order:\n"
    total = 0
    for pid, qty in cart.items():
        p = Product.query.get(int(pid))
        if p:
            subtotal = p.price * qty
            total += subtotal
            msg += f"- {p.title} x{qty} = Rs.{int(subtotal)}\n"
    msg += f"\nTotal: Rs.{int(total)}"
    wa_url = f"https://wa.me/923127891021?text={urllib.parse.quote(msg)}"
    return redirect(wa_url)

if __name__ == "__main__":
    app.run(debug=True)
