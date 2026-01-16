from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from .db import db
from .models import Product, Order, User
from .utils import admin_required, current_user

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/")
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "products": Product.query.count(),
        "orders": Order.query.count(),
    }
    latest_orders = Order.query.order_by(Order.id.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, latest_orders=latest_orders)


# -------------------------
# Товары
# -------------------------

@bp.get("/products")
@admin_required
def products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin/products.html", products=products)


@bp.get("/products/new")
@admin_required
def product_new():
    return render_template("admin/product_form.html", p=None)


@bp.post("/products/new")
@admin_required
def product_new_post():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    price = int(request.form.get("price", 0) or 0)
    category = request.form.get("category", "Другое").strip() or "Другое"
    image_url = request.form.get("image_url", "").strip()
    is_active = True if request.form.get("is_active") == "on" else False

    if not title:
        flash("Название обязательно.", "warning")
        return redirect(url_for("admin.product_new"))

    p = Product(
        title=title,
        description=description,
        price=price,
        category=category,
        image_url=image_url,
        is_active=is_active,
    )
    db.session.add(p)
    db.session.commit()
    flash("Товар добавлен.", "success")
    return redirect(url_for("admin.products"))


@bp.get("/products/<int:pid>/edit")
@admin_required
def product_edit(pid: int):
    p = db.session.get(Product, pid)
    if not p:
        flash("Товар не найден.", "warning")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", p=p)


@bp.post("/products/<int:pid>/edit")
@admin_required
def product_edit_post(pid: int):
    p = db.session.get(Product, pid)
    if not p:
        flash("Товар не найден.", "warning")
        return redirect(url_for("admin.products"))

    p.title = request.form.get("title", "").strip()
    p.description = request.form.get("description", "").strip()
    p.price = int(request.form.get("price", 0) or 0)
    p.category = request.form.get("category", "Другое").strip() or "Другое"
    p.image_url = request.form.get("image_url", "").strip()
    p.is_active = True if request.form.get("is_active") == "on" else False

    db.session.commit()
    flash("Изменения сохранены.", "success")
    return redirect(url_for("admin.products"))


@bp.post("/products/<int:pid>/delete")
@admin_required
def product_delete(pid: int):
    p = db.session.get(Product, pid)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash("Товар удалён.", "info")
    return redirect(url_for("admin.products"))


# -------------------------
# Заказы
# -------------------------

@bp.get("/orders")
@admin_required
def orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("admin/orders.html", orders=orders)


# -------------------------
# Пользователи
# -------------------------

@bp.get("/users")
@admin_required
def users():
    q = request.args.get("q", "").strip()
    role = request.args.get("role", "").strip()  # user/admin/""(all)

    query = User.query
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    if role in ("user", "admin"):
        query = query.filter_by(role=role)

    users = query.order_by(User.id.desc()).all()
    return render_template("admin/users.html", users=users, q=q, role=role)


@bp.get("/users/<int:uid>/edit")
@admin_required
def user_edit(uid: int):
    u = db.session.get(User, uid)
    if not u:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", u=u)


@bp.post("/users/<int:uid>/edit")
@admin_required
def user_edit_post(uid: int):
    u = db.session.get(User, uid)
    if not u:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("admin.users"))

    me = current_user()
    new_role = (request.form.get("role") or "").strip()
    new_password = (request.form.get("password") or "").strip()

    if new_role not in ("user", "admin"):
        flash("Некорректная роль.", "warning")
        return redirect(url_for("admin.user_edit", uid=uid))

    # Нельзя удалить последнего админа (защита от потери доступа)
    if u.role == "admin" and new_role != "admin":
        admins = User.query.filter_by(role="admin").count()
        if admins <= 1:
            flash("Нельзя снять роль администратора с последнего администратора.", "danger")
            return redirect(url_for("admin.user_edit", uid=uid))

    # Если меняем свою роль -> тоже проверяем, что не последний админ
    if me and me.id == u.id and u.role == "admin" and new_role != "admin":
        admins = User.query.filter_by(role="admin").count()
        if admins <= 1:
            flash("Нельзя снять роль администратора с самого себя (вы последний админ).", "danger")
            return redirect(url_for("admin.user_edit", uid=uid))

    u.role = new_role

    if new_password:
        if len(new_password) < 6:
            flash("Пароль должен быть минимум 6 символов.", "warning")
            return redirect(url_for("admin.user_edit", uid=uid))
        u.password_hash = generate_password_hash(new_password)

    db.session.commit()
    flash("Пользователь обновлён.", "success")
    return redirect(url_for("admin.users"))


@bp.post("/users/<int:uid>/delete")
@admin_required
def user_delete(uid: int):
    u = db.session.get(User, uid)
    if not u:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("admin.users"))

    me = current_user()
    if me and me.id == u.id:
        flash("Нельзя удалить самого себя.", "danger")
        return redirect(url_for("admin.users"))

    # Нельзя удалить последнего админа
    if u.role == "admin":
        admins = User.query.filter_by(role="admin").count()
        if admins <= 1:
            flash("Нельзя удалить последнего администратора.", "danger")
            return redirect(url_for("admin.users"))

    # если у пользователя есть заказы — лучше не удалять (иначе можно потерять историю)
    if Order.query.filter_by(user_id=u.id).count() > 0:
        flash("Нельзя удалить пользователя: у него есть заказы. Сначала удалите/очистите заказы.", "warning")
        return redirect(url_for("admin.users"))

    db.session.delete(u)
    db.session.commit()
    flash("Пользователь удалён.", "info")
    return redirect(url_for("admin.users"))


@bp.get("/users/<int:uid>/orders")
@admin_required
def user_orders(uid: int):
    u = db.session.get(User, uid)
    if not u:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("admin.users"))

    orders = Order.query.filter_by(user_id=u.id).order_by(Order.id.desc()).all()
    return render_template("admin/user_orders.html", u=u, orders=orders)