from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import db
from .models import Product, Order, OrderItem
from .utils import (
    current_user,
    login_required,
    cart_items,
    add_to_cart,
    remove_from_cart,
    clear_cart,
)

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    products = Product.query.filter_by(is_active=True).limit(6).all()
    return render_template("home.html", products=products)


@bp.get("/about")
def about():
    return render_template("about.html")


@bp.get("/contacts")
def contacts():
    return render_template("contacts.html")


@bp.get("/catalog")
def catalog():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    query = Product.query.filter_by(is_active=True)
    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))
    if category:
        query = query.filter_by(category=category)

    products = query.order_by(Product.id.desc()).all()
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    return render_template("catalog.html", products=products, categories=categories, q=q, category=category)


@bp.get("/product/<int:pid>")
def product(pid: int):
    p = db.session.get(Product, pid)
    if not p or not p.is_active:
        flash("Товар не найден.", "warning")
        return redirect(url_for("main.catalog"))
    return render_template("product.html", p=p)


@bp.post("/cart/add/<int:pid>")
def cart_add(pid: int):
    p = db.session.get(Product, pid)
    if not p or not p.is_active:
        flash("Товар недоступен.", "warning")
        return redirect(url_for("main.catalog"))

    add_to_cart(pid, qty=1)
    flash("Добавлено в корзину.", "success")
    return redirect(request.referrer or url_for("main.cart"))


@bp.post("/cart/remove/<int:pid>")
def cart_remove(pid: int):
    remove_from_cart(pid)
    flash("Удалено из корзины.", "info")
    return redirect(url_for("main.cart"))


@bp.post("/cart/clear")
def cart_clear():
    clear_cart()
    flash("Корзина очищена.", "info")
    return redirect(url_for("main.cart"))


@bp.get("/cart")
def cart():
    items, total = cart_items()
    return render_template("cart.html", items=items, total=total)


@bp.get("/checkout")
@login_required
def checkout():
    items, total = cart_items()
    if not items:
        flash("Корзина пустая.", "warning")
        return redirect(url_for("main.catalog"))
    return render_template("checkout.html", items=items, total=total)


@bp.post("/checkout")
@login_required
def checkout_post():
    items, total = cart_items()
    if not items:
        flash("Корзина пустая.", "warning")
        return redirect(url_for("main.catalog"))

    u = current_user()
    order = Order(user_id=u.id, total=total, status="принят")
    db.session.add(order)
    db.session.flush()

    for it in items:
        p = it["product"]
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=p.id,
                title=p.title,
                price=p.price,
                qty=it["qty"],
            )
        )

    db.session.commit()

    # ✅ очистить корзину пользователя (в БД)
    clear_cart()

    flash(f"Заказ №{order.id} оформлен!", "success")
    return redirect(url_for("main.account"))


@bp.get("/account")
@login_required
def account():
    u = current_user()
    orders = Order.query.filter_by(user_id=u.id).order_by(Order.id.desc()).all()
    return render_template("account/dashboard.html", u=u, orders=orders)
