from functools import wraps
from flask import session, redirect, url_for, flash, request
from .db import db
from .models import User, Product, CartItem


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Нужно войти в систему.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        u = current_user()
        if not u or u.role != "admin":
            flash("Доступ только для администратора.", "danger")
            return redirect(url_for("main.home"))
        return view(*args, **kwargs)

    return wrapped


# -------------------------
# Корзина
# -------------------------

def get_session_cart():
    # {product_id(str): qty(int)}
    return session.setdefault("cart", {})


def cart_count():
    """Количество единиц товаров в корзине (бейдж в хедере)."""
    u = current_user()
    if u:
        return int(
            db.session.query(db.func.coalesce(db.func.sum(CartItem.qty), 0))
            .filter(CartItem.user_id == u.id)
            .scalar()
            or 0
        )
    cart = session.get("cart", {})
    return sum(int(qty) for qty in cart.values())


def cart_items():
    """Возвращает (items, total) для отображения корзины/оформления.
    items: [{product, qty, line}]
    """
    u = current_user()
    items = []
    total = 0

    if u:
        rows = CartItem.query.filter(CartItem.user_id == u.id).all()
        for row in rows:
            p = row.product
            if not p or not p.is_active:
                continue
            qty = int(row.qty)
            line = p.price * qty
            total += line
            items.append({"product": p, "qty": qty, "line": line})
        return items, total

    cart = session.get("cart", {})
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        p = db.session.get(Product, pid)
        if not p or not p.is_active:
            continue
        qty = int(qty)
        line = p.price * qty
        total += line
        items.append({"product": p, "qty": qty, "line": line})
    return items, total


def add_to_cart(product_id: int, qty: int = 1):
    """Добавить товар в корзину (в БД для авторизованных, иначе в сессию)."""
    u = current_user()
    if u:
        row = CartItem.query.filter_by(user_id=u.id, product_id=product_id).first()
        if row:
            row.qty = int(row.qty) + int(qty)
        else:
            db.session.add(CartItem(user_id=u.id, product_id=product_id, qty=int(qty)))
        db.session.commit()
        return

    cart = get_session_cart()
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + int(qty)
    session.modified = True


def remove_from_cart(product_id: int):
    """Удалить позицию из корзины."""
    u = current_user()
    if u:
        CartItem.query.filter_by(user_id=u.id, product_id=product_id).delete()
        db.session.commit()
        return

    cart = get_session_cart()
    cart.pop(str(product_id), None)
    session.modified = True


def clear_cart():
    """Очистить корзину."""
    u = current_user()
    if u:
        CartItem.query.filter_by(user_id=u.id).delete()
        db.session.commit()
        return
    session["cart"] = {}
    session.modified = True


def merge_session_cart_into_db(user_id: int):
    """Слить корзину гостя (session) в корзину пользователя (DB)."""
    cart = session.get("cart") or {}
    if not cart:
        return
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            qty = int(qty)
        except Exception:
            continue
        if qty <= 0:
            continue
        row = CartItem.query.filter_by(user_id=user_id, product_id=pid).first()
        if row:
            row.qty = int(row.qty) + qty
        else:
            db.session.add(CartItem(user_id=user_id, product_id=pid, qty=qty))
    db.session.commit()
    session["cart"] = {}
    session.modified = True


# -------------------------
# Совместимость со старым кодом (get_cart)
# -------------------------

from collections.abc import MutableMapping

class _DBCartProxy(MutableMapping):
    """Dict-подобная корзина для авторизованного пользователя.
    Нужна для совместимости со старой логикой, где использовали get_cart()[pid]=qty.
    В новой логике лучше использовать add_to_cart/remove_from_cart/clear_cart.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id

    def _rows(self):
        return CartItem.query.filter_by(user_id=self.user_id).all()

    def _get_row(self, pid: int):
        return CartItem.query.filter_by(user_id=self.user_id, product_id=pid).first()

    def __getitem__(self, key):
        pid = int(key)
        row = self._get_row(pid)
        if not row:
            raise KeyError(key)
        return int(row.qty)

    def __setitem__(self, key, value):
        pid = int(key)
        qty = int(value)
        if qty <= 0:
            self.__delitem__(key)
            return
        row = self._get_row(pid)
        if row:
            row.qty = qty
        else:
            db.session.add(CartItem(user_id=self.user_id, product_id=pid, qty=qty))
        db.session.commit()

    def __delitem__(self, key):
        pid = int(key)
        CartItem.query.filter_by(user_id=self.user_id, product_id=pid).delete()
        db.session.commit()

    def __iter__(self):
        for row in self._rows():
            yield str(row.product_id)

    def __len__(self):
        return len(self._rows())


def get_cart():
    """Совместимость: возвращает dict корзины.
    Для гостей — session['cart'], для авторизованных — proxy поверх таблицы CartItem.
    """
    u = current_user()
    if u:
        return _DBCartProxy(u.id)
    return get_session_cart()
