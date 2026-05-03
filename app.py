from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
import json, os, urllib.parse, random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "annahenna2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

ADMIN_PASSWORD = "anna1234"
CATEGORIES = ["Mehndi Stickers","Mehndi Cones","Wall Art & CO2 Laser","Marbles & Bangles","🔥 Deals","Other"]

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(500))
    link = db.Column(db.String(500))
    vendor = db.Column(db.String(100))
    category = db.Column(db.String(100), default="Mehndi Stickers")

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    page = db.Column(db.String(200))
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

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
                    title=p["title"], price=price,
                    image=p.get("local_image", ""),
                    link=p["link"], vendor=p.get("vendor", ""),
                    category=p.get("category", "Mehndi Stickers")
                ))
            db.session.commit()

def track_visitor(page):
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip: ip = ip.split(',')[0].strip()
        import urllib.request
        location = json.loads(urllib.request.urlopen(f'http://ip-api.com/json/{ip}', timeout=2).read())
        db.session.add(Visitor(ip=ip, country=location.get('country','Unknown'),
            city=location.get('city','Unknown'), page=page))
        db.session.commit()
    except: pass

def admin_required():
    return session.get("admin_logged_in")

@app.route("/")
def index():
    track_visitor('/')
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    query = Product.query
    if search: query = query.filter(Product.title.ilike(f"%{search}%"))
    if category: query = query.filter(Product.category == category)
    products = query.order_by(Product.id.desc()).all()
    all_with_img = Product.query.filter(Product.image != "").all()
    featured = random.sample(all_with_img, min(5, len(all_with_img)))
    return render_template("index.html", products=products, search=search,
                         featured=featured, categories=CATEGORIES, active_category=category)

@app.route("/category/<cat>")
def category(cat):
    track_visitor(f'/category/{cat}')
    products = Product.query.filter(Product.category == cat).order_by(Product.id.desc()).all()
    all_with_img = Product.query.filter(Product.image != "").all()
    featured = random.sample(all_with_img, min(5, len(all_with_img)))
    return render_template("index.html", products=products, search="",
                         featured=featured, categories=CATEGORIES, active_category=cat)

@app.route("/about")
def about():
    track_visitor('/about')
    return render_template("about.html")

@app.route("/contact")
def contact():
    track_visitor('/contact')
    return render_template("contact.html")

@app.route("/product/<int:id>")
def product(id):
    track_visitor(f'/product/{id}')
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
    visitors = Visitor.query.order_by(Visitor.visited_at.desc()).limit(50).all()
    total_visitors = Visitor.query.count()
    today_visitors = Visitor.query.filter(
        db.func.date(Visitor.visited_at) == datetime.utcnow().date()).count()
    return render_template("admin_dashboard.html", products=products,
                         visitors=visitors, total_visitors=total_visitors,
                         today_visitors=today_visitors)

@app.route("/admin/visitors")
def admin_visitors():
    if not admin_required():
        return redirect(url_for("admin_login"))
    visitors = Visitor.query.order_by(Visitor.visited_at.desc()).all()
    total = Visitor.query.count()
    return render_template("visitors.html", visitors=visitors, total=total)

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if not admin_required():
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        try:
            price = float(request.form.get("price", 0))
        except:
            price = 0
        title = request.form.get("title", "")
        product = Product(
            title=title, price=price,
            image=request.form.get("image", ""),
            link=request.form.get("link", ""),
            vendor=request.form.get("vendor", ""),
            category=request.form.get("category", "Mehndi Stickers")
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_add.html", categories=CATEGORIES)

@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def admin_edit(id):
    if not admin_required():
        return redirect(url_for("admin_login"))
    p = Product.query.get_or_404(id)
    if request.method == "POST":
        p.title = request.form.get("title")
        p.price = float(request.form.get("price", 0))
        p.vendor = request.form.get("vendor", "")
        p.category = request.form.get("category", "Mehndi Stickers")
        if request.form.get("image"):
            p.image = request.form.get("image")
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit.html", product=p, categories=CATEGORIES)

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
