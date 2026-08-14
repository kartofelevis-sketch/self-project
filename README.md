# SELF

Study → Explore → Learn → Flourish.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

copy .env.example .env       # Windows, или cp .env.example .env
# впиши свои SECRET_KEY и BOT_API_KEY
# DATABASE_URL можно не трогать — там уже правильный относительный путь.
# Если решишь его переопределить: НЕ пиши "instance/" сама — Flask-SQLAlchemy
# сам подставляет папку instance/ перед относительным путём, иначе получится
# instance/instance/self.db и flask init-db упадёт с "unable to open database file".

flask init-db
flask seed-db
flask run
```

Открыть: http://127.0.0.1:5000

## Структура базы

```
Section (study / explore / learn / flourish)
   └── Subsection (тематическая рубрика внутри раздела)
          └── Post (текст в markdown, теги, обложка, статус публикации)
```

- **Section** — 4 фиксированных раздела философии SELF. Хранит `accent` —
  hex-цвет, который использует фронт (карточки, бейджи).
- **Subsection** — рубрика внутри раздела ("Как учиться", "Инструменты"...).
  Это то, что видно в боковом меню на странице раздела и то, что бот
  предложит выбрать при публикации поста.
- **Post** — сама единица контента. `content_type` заложен на будущее
  (сейчас только `text`, потом можно `video`/`gallery`/`audio` без изменения
  схемы). `source` и `telegram_message_id` нужны, чтобы бот мог опознать
  "своё" сообщение и отредактировать/удалить пост повторно, а не плодить
  дубликаты при редактировании поста в Telegram.
- **Tag** — сквозные теги поверх рубрик, many-to-many через `post_tags`.

## Как бот будет публиковать посты

Сайт ничего не знает про Telegram — это просто JSON API с авторизацией по
заголовку `X-API-Key` (см. `BOT_API_KEY` в `.env`). Бот — отдельный проект,
он просто дергает эти эндпоинты:

- `GET /api/sections` — получить список разделов и подразделов (построить
  меню выбора рубрики в боте).
- `POST /api/subsections` — создать новую рубрику на лету, если для темы
  поста ещё нет подходящей.
- `POST /api/posts` — опубликовать пост.
- `PATCH /api/posts/<id>` — отредактировать (например, если ты правишь то
  же сообщение в Telegram).
- `DELETE /api/posts/<id>` — удалить.

Пример вызова из бота (aiogram/requests — не важно, любой HTTP-клиент):

```python
import requests

requests.post(
    "https://твой-домен/api/posts",
    headers={"X-API-Key": "тот-же-ключ-что-в-.env"},
    json={
        "subsection_id": 3,
        "title": "Название поста",
        "content": "Текст в **markdown**",
        "summary": "Короткий анонс",
        "tags": ["продуктивность"],
        "telegram_message_id": update.message.message_id,
    },
)
```

Схема специально плоская (без Flask-Admin/авторизации пользователей) —
единственный "автор" контента сейчас это ты через бота или напрямую через
консоль (`flask shell`, работа с `db.session`). Если позже понадобится
веб-панель для ручного редактирования — её можно добавить поверх тех же
моделей, ничего не меняя в схеме.

## Дальше

- Добавить `Flask-Migrate`, когда схема начнёт меняться после первого деплоя
  (сейчас `flask init-db` просто создаёт таблицы с нуля).
- Когда появится не-текстовый контент — расширить рендер в `post.html` по
  `post.content_type`.
