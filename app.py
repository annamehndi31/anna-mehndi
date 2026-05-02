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
