import sys
import socket
from werkzeug.security import generate_password_hash
from shop import create_app
from shop.db import db
from shop.models import User, Product


def init_db(app):
    with app.app_context():
        db.create_all()
    print("DB initialized.")


def seed(app):
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            db.session.add(
                User(username="admin", password_hash=generate_password_hash("admin123"), role="admin")
            )
        if not User.query.filter_by(username="user").first():
            db.session.add(
                User(username="user", password_hash=generate_password_hash("user123"), role="user")
            )

        if Product.query.count() == 0:
            demo = [
                Product(title="Беспроводные наушники", description="Шумоподавление, 20 часов работы.", price=3990, category="Электроника",
                        image_url="https://i-store.net/_sh/73/7328.jpg"),
                Product(title="Рюкзак городской", description="Водостойкий, отделение для ноутбука 15.6 дюйма.", price=2490, category="Аксессуары",
                        image_url="https://www.blacksides.ru/upload/resize_cache/iblock/b2f/998_2500_1/b2f402a154e82d1af1c88e49f11372c6.jpg"),
                Product(title="Кружка термо", description="Держит тепло до 6 часов.", price=890, category="Дом",
                        image_url="https://nadoba.ru/upload/import_data/images/content/flasks/juta/735311_1juta_thermal_mug_mint.jpg"),
                Product(title="Фитнес-браслет", description="Пульс, сон, шаги, уведомления.", price=1990, category="Электроника",
                        image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTW7e01Dk3J7UioNsA6aevygAxhpGv3Ikj8fQ&s"),
            ]
            db.session.add_all(demo)

        db.session.commit()
    print("Seed complete. Users: admin/admin123, user/user123")


def get_local_ip():
    """Пытаемся определить IP компьютера в локальной сети (для ссылки на телефон)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Подключение не реально отправляет данные, нужно только чтобы ОС выбрала интерфейс
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def main():
    app = create_app()
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "run").lower()

    if cmd in ("run", "serve"):
        # Слушаем на всех интерфейсах, чтобы открывалось с телефона по IP
        host = "0.0.0.0"
        port = 5000

        ip = get_local_ip() or "192.168.88.186"  # запасной вариант (можешь заменить на свой)
        print("\nСсылки для открытия:")
        print(f"ПК:      http://127.0.0.1:{port}")
        print(f"Телефон: http://{ip}:{port}  (телефон и ПК должны быть в одной Wi-Fi сети)\n")

        app.run(host=host, port=port, debug=True)
        return

    if cmd in ("init-db", "initdb", "db"):
        init_db(app)
        return

    if cmd in ("seed", "demo"):
        seed(app)
        return

    print("Unknown command:", cmd)
    print("Usage:")
    print("  python run.py run")
    print("  python run.py init-db")
    print("  python run.py seed")


if __name__ == "__main__":
    main()
