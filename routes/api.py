from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from slugify import slugify

from extensions import db
from models import Section, Subsection, Post, Tag

bp = Blueprint("api", __name__, url_prefix="/api")


def require_bot_key(fn):
    """Простая авторизация по заголовку X-API-Key. Ключ задаётся в .env
    (BOT_API_KEY) и хранится в конфиге бота — он же его отправляет."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key or key != current_app.config["BOT_API_KEY"]:
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper


def unique_slug(base):
    slug = slugify(base)
    candidate = slug
    i = 2
    while Post.query.filter_by(slug=candidate).first() is not None:
        candidate = f"{slug}-{i}"
        i += 1
    return candidate


@bp.route("/sections", methods=["GET"])
@require_bot_key
def list_sections():
    """Бот дергает это, чтобы построить меню: раздел -> подразделы."""
    sections = Section.query.order_by(Section.order).all()
    return jsonify([
        {
            "id": s.id,
            "slug": s.slug,
            "name": s.name,
            "subsections": [
                {"id": sub.id, "slug": sub.slug, "name": sub.name}
                for sub in s.subsections
            ],
        }
        for s in sections
    ])


@bp.route("/subsections", methods=["POST"])
@require_bot_key
def create_subsection():
    """Если для новой темы ещё нет подраздела — бот может создать его на лету."""
    data = request.get_json(force=True) or {}
    section = Section.query.filter_by(slug=data.get("section_slug")).first()
    if not section:
        return jsonify({"error": "unknown section_slug"}), 400

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    subsection = Subsection(
        section_id=section.id,
        slug=slugify(name),
        name=name,
        order=len(section.subsections),
    )
    db.session.add(subsection)
    db.session.commit()
    return jsonify({"id": subsection.id, "slug": subsection.slug, "name": subsection.name}), 201


@bp.route("/posts", methods=["POST"])
@require_bot_key
def create_post():
    """
    Ожидаемое тело запроса от бота:
    {
      "subsection_id": 3,
      "title": "...",
      "content": "... markdown ...",
      "summary": "...",                 # опционально
      "content_type": "text",           # опционально, по умолчанию text
      "cover_image_url": "...",         # опционально
      "tags": ["продуктивность"],        # опционально
      "telegram_message_id": 12345,     # опционально, для будущего редактирования
      "publish": true                   # опционально, по умолчанию true
    }
    """
    data = request.get_json(force=True) or {}

    subsection = Subsection.query.get(data.get("subsection_id"))
    if not subsection:
        return jsonify({"error": "unknown subsection_id"}), 400

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    post = Post(
        subsection_id=subsection.id,
        title=title,
        slug=unique_slug(title),
        summary=data.get("summary"),
        content=content,
        content_type=data.get("content_type", "text"),
        cover_image_url=data.get("cover_image_url"),
        source="bot",
        telegram_message_id=data.get("telegram_message_id"),
        published=data.get("publish", True),
    )

    for tag_name in data.get("tags", []):
        tag_slug = slugify(tag_name)
        tag = Tag.query.filter_by(slug=tag_slug).first()
        if not tag:
            tag = Tag(slug=tag_slug, name=tag_name)
            db.session.add(tag)
        post.tags.append(tag)

    db.session.add(post)
    db.session.commit()

    return jsonify({"id": post.id, "slug": post.slug}), 201


@bp.route("/posts/<int:post_id>", methods=["PATCH"])
@require_bot_key
def update_post(post_id):
    """Правка поста — например, бот редактирует то же сообщение в Telegram."""
    post = Post.query.get_or_404(post_id)
    data = request.get_json(force=True) or {}

    for field in ("title", "summary", "content", "content_type", "cover_image_url", "published"):
        if field in data:
            setattr(post, field, data[field])

    db.session.commit()
    return jsonify({"id": post.id, "slug": post.slug})


@bp.route("/posts/<int:post_id>", methods=["DELETE"])
@require_bot_key
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"deleted": post_id})
