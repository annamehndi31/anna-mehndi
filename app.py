from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
import json, os, urllib.parse, random

app = Flask(__name__)
app.secret_key = "annahenna2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

ADMIN_PASSWORD = "anna1234"

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

def admin_required():
    return session.get("admin_logged_in")

@app.route("/")
def index():
    search = request.args.get("search", "")
    if search:
        products = Product.query.filter(Product.title.ilike(f"%{search}%")).order_by(Product.id.desc()).all()
    else:
        products = Product.query.order_by(Product.id.desc()).all()
    all_products = Product.query.filter(Product.image != "").all()
    featured = random.sample(all_products, min(5, len(all_products)))
    return render_template("index.html", products=products, search=search, featured=featured)

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
    items = []
    total = 0
    for pid, qty in cart.items():
        p = Product.query.get(int(pid))
        if p:
            subtotal = p.price * qty
            items.append({"product": p, "qty": qty, "subtotal": subtotal})
            total += subtotal
    return render_template("checkout.html", items=items, subtotal=total)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Wrong password!")
    return render_template("admin_login.html", error=None)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))

@app.route("/admin")
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("admin_login"))
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin_dashboard.html", products=products)

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if not admin_required():
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        try:
            price = float(request.form.get("price", 0))
        except:
            price = 0
        image_url = request.form.get("image", "")
        title = request.form.get("title", "")
        auto_link = f"https://web-production-8b9ae.up.railway.app/products/{title.lower().replace(' ', '-')}"
        product = Product(
            title=title,
            price=price,
            image=image_url,
            link=request.form.get("link") or auto_link,
            vendor=request.form.get("vendor", "")
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_add.html")

@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def admin_edit(id):
    if not admin_required():
        return redirect(url_for("admin_login"))
    p = Product.query.get_or_404(id)
    if request.method == "POST":
        p.title = request.form.get("title")
        p.price = float(request.form.get("price", 0))
        p.vendor = request.form.get("vendor", "")
        if request.form.get("image"):
            p.image = request.form.get("image")
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit.html", product=p)

@app.route("/admin/delete/<int:id>")
def admin_delete(id):
    if not admin_required():
        return redirect(url_for("admin_login"))
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
