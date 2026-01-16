import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from .db import db
from .models import User, Product

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Создать таблицы БД."""
    db.create_all()
    click.echo("DB initialized.")

@click.command("seed")
@with_appcontext
def seed_command():
    """Создать тестовых пользователей и товары."""
    # Пользователи
    if not User.query.filter_by(username="admin").first():
        db.session.add(User(username="admin", password_hash=generate_password_hash("admin123"), role="admin"))
    if not User.query.filter_by(username="user").first():
        db.session.add(User(username="user", password_hash=generate_password_hash("user123"), role="user"))

    # Товары
    if Product.query.count() == 0:
        demo = [
            Product(title="Беспроводные наушники", description="Шумоподавление, 20 часов работы.", price=3990, category="Электроника",
                    image_url="https://picsum.photos/seed/headphones/800/600"),
            Product(title="Рюкзак городской", description="Водостойкий, отделение для ноутбука 15.6 дюйма.", price=2490, category="Аксессуары",
                    image_url="https://picsum.photos/seed/backpack/800/600"),
            Product(title="Кружка термо", description="Держит тепло до 6 часов.", price=890, category="Дом",
                    image_url="https://picsum.photos/seed/mug/800/600"),
            Product(title="Фитнес-браслет", description="Пульс, сон, шаги, уведомления.", price=1990, category="Электроника",
                    image_url="https://picsum.photos/seed/band/800/600"),
        ]
        db.session.add_all(demo)

    db.session.commit()
    click.echo("Seed complete. Users: admin/admin123, user/user123")
