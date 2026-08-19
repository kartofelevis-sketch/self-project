import os

import markdown as md
from flask import Flask

from config import Config
from extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # instance/ не хранится в git и в zip-архивах (пустые папки туда не
    # попадают), поэтому создаём её сами, если её нет — иначе SQLite не
    # сможет создать файл базы.
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)

    from routes.main import bp as main_bp
    from routes.sections import bp as sections_bp
    from routes.api import bp as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(sections_bp)
    app.register_blueprint(api_bp)

    @app.template_filter("markdown")
    def markdown_filter(text):
        return md.markdown(text or "", extensions=["extra", "sane_lists"])

    register_cli(app)
    return app


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """flask init-db — создать таблицы."""
        db.create_all()
        print("База данных создана.")

    @app.cli.command("seed-db")
    def seed_db():
        """flask seed-db — наполнить базу разделами SELF и примерами постов."""
        from seed import run_seed

        run_seed()
        print("Начальные данные добавлены.")


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
