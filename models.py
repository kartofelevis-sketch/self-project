from datetime import datetime

from extensions import db

# Пост может иметь несколько тегов, тег — принадлежать многим постам.
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class Section(db.Model):
    """
    Один из 4 разделов философии SELF: study / explore / learn / flourish.
    Плюс служебный раздел "about" не хранится тут — это статическая страница
    (routes/main.py), т.к. у неё нет подразделов и постов.
    """

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(32), unique=True, nullable=False)      # study / explore / learn / flourish
    name = db.Column(db.String(64), nullable=False)                    # "Study"
    tagline = db.Column(db.String(255))                                 # короткий подзаголовок
    description = db.Column(db.Text)
    accent = db.Column(db.String(16), default="#3B5169")                # HEX цвет раздела для фронта
    order = db.Column(db.Integer, default=0)

    subsections = db.relationship(
        "Subsection", backref="section", order_by="Subsection.order",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Section {self.slug}>"


class Subsection(db.Model):
    """
    Тематическая рубрика внутри раздела, например:
    Study -> "Как учиться", "Инструменты", "Дисциплина".
    Ровно то, что бот будет предлагать выбрать при публикации поста.
    """

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=False)
    slug = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    posts = db.relationship(
        "Post", backref="subsection", order_by="Post.published_at.desc()",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint("section_id", "slug", name="uq_subsection_slug_per_section"),
    )

    def __repr__(self):
        return f"<Subsection {self.section.slug}/{self.slug}>"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)


class Post(db.Model):
    """
    Единица контента. Сейчас формат только text/markdown, но content_type
    заложен заранее — когда появится видео/подкаст/галерея, не придётся
    менять схему, просто добавится новый тип и способ рендера в шаблоне.
    """

    id = db.Column(db.Integer, primary_key=True)
    subsection_id = db.Column(db.Integer, db.ForeignKey("subsection.id"), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    summary = db.Column(db.String(500))                # короткий анонс для карточек/превью
    content = db.Column(db.Text, nullable=False)        # markdown

    content_type = db.Column(db.String(16), default="text")   # text | video | audio | gallery
    cover_image_url = db.Column(db.String(512))

    author = db.Column(db.String(128), default="SELF")
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Откуда пришёл пост и id сообщения в Telegram — нужно, чтобы бот мог
    # позже найти и отредактировать/удалить именно этот пост по повторному
    # апдейту того же сообщения, а не плодить дубликаты.
    source = db.Column(db.String(16), default="web")          # web | bot
    telegram_message_id = db.Column(db.BigInteger, index=True, nullable=True)

    tags = db.relationship("Tag", secondary=post_tags, backref="posts")

    @property
    def section(self):
        return self.subsection.section

    def __repr__(self):
        return f"<Post {self.slug}>"
