import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # SQLite по умолчанию — файл базы лежит в instance/self.db (абсолютный путь).
    # Если переопределяешь DATABASE_URL относительным путём в .env — не пиши
    # "instance/" сама: Flask-SQLAlchemy сам подставляет instance/ перед
    # относительным путём, иначе получится instance/instance/self.db.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'self.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ключ, которым бот авторизуется при вызове /api/*
    BOT_API_KEY = os.environ.get("BOT_API_KEY", "dev-bot-key-change-me")

    POSTS_PER_PAGE = 12
