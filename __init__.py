from pathlib import Path
from flask import Flask

from .db import db
from .main import bp as main_bp
from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .cli import init_db_command, seed_command


def create_app():
    base_dir = Path(__file__).resolve().parent.parent  # папка проекта (где run.py)
    templates_dir = base_dir / "templates"
    static_dir = base_dir / "static"

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    # instance для SQLite
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db_path = (Path(app.instance_path) / "shop.sqlite3").resolve()

    app.config.update(
        SECRET_KEY="dev-secret-change-me",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_command)

    from .utils import current_user, cart_count
    app.jinja_env.globals.update(current_user=current_user, cart_count=cart_count)

    return app
