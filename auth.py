from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db
from .models import User
from .utils import merge_session_cart_into_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/login")
def login():
    return render_template("auth/login.html")


@bp.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        flash("Неверный логин или пароль.", "danger")
        return redirect(url_for("auth.login"))

    session["user_id"] = user.id
    # ✅ корзина гостя -> в БД пользователю
    merge_session_cart_into_db(user.id)

    flash("Добро пожаловать!", "success")
    next_url = request.args.get("next")
    return redirect(next_url or url_for("main.home"))


@bp.get("/register")
def register():
    return render_template("auth/register.html")


@bp.post("/register")
def register_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or len(username) < 3:
        flash("Логин должен быть минимум 3 символа.", "warning")
        return redirect(url_for("auth.register"))
    if not password or len(password) < 6:
        flash("Пароль должен быть минимум 6 символов.", "warning")
        return redirect(url_for("auth.register"))
    if User.query.filter_by(username=username).first():
        flash("Такой логин уже занят.", "danger")
        return redirect(url_for("auth.register"))

    user = User(username=username, password_hash=generate_password_hash(password), role="user")
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    # ✅ корзина гостя -> в БД пользователю
    merge_session_cart_into_db(user.id)

    flash("Аккаунт создан!", "success")
    return redirect(url_for("main.home"))


@bp.post("/logout")
def logout():
    session.pop("user_id", None)
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("main.home"))
