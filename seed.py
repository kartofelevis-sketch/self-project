from datetime import datetime

from extensions import db
from models import Section, Subsection, Post

SECTIONS = [
    {
        "slug": "study",
        "name": "Study",
        "tagline": "Начни с системы",
        "description": "Фундамент: как учиться эффективно и превращать хаос информации в систему.",
        "accent": "#5B2A7A",
        "subsections": [
            ("Как учиться", "Методы, принципы, ошибки"),
            ("Инструменты", "Приложения и техники для учёбы"),
        ],
    },
    {
        "slug": "explore",
        "name": "Explore",
        "tagline": "Исследуй новые идеи и возможности",
        "description": "Расширение кругозора: новые области, эксперименты, нестандартные идеи и решения.",
        "accent": "#8B3FA8",
        "subsections": [
            ("Идеи", "Концепции, которые стоит попробовать"),
            ("Возможности", "Куда можно приложить силы"),
        ],
    },
    {
        "slug": "learn",
        "name": "Learn",
        "tagline": "Превращай знания в реальные навыки",
        "description": "От теории к практике: как закрепить и применить то, что изучил.",
        "accent": "#B15AC4",
        "subsections": [
            ("Практика", "Упражнения и разборы"),
            ("Проекты", "Как довести дело до результата"),
        ],
    },
    {
        "slug": "flourish",
        "name": "Flourish",
        "tagline": "Раскрывай потенциал и достигай успеха",
        "description": "Итог цикла: рост, результаты, следующая цель.",
        "accent": "#E08FD1",
        "subsections": [
            ("Истории", "Примеры и разборы результатов"),
            ("Рост", "Долгосрочные привычки и цели"),
        ],
    },
]


def run_seed():
    for s in SECTIONS:
        section = Section.query.filter_by(slug=s["slug"]).first()
        if not section:
            section = Section(
                slug=s["slug"],
                name=s["name"],
                tagline=s["tagline"],
                description=s["description"],
                accent=s["accent"],
                order=len(db.session.query(Section).all()),
            )
            db.session.add(section)
            db.session.flush()
        else:
            # раздел уже существует — подтягиваем актуальный текст/цвет
            # из SECTIONS, чтобы повторный flask seed-db подхватывал правки
            section.name = s["name"]
            section.tagline = s["tagline"]
            section.description = s["description"]
            section.accent = s["accent"]

        for order, (name, desc) in enumerate(s["subsections"]):
            slug = name.lower().replace(" ", "-")
            sub = Subsection.query.filter_by(section_id=section.id, slug=slug).first()
            if not sub:
                sub = Subsection(
                    section_id=section.id, slug=slug, name=name, description=desc, order=order
                )
                db.session.add(sub)
                db.session.flush()

            if not sub.posts:
                post = Post(
                    subsection_id=sub.id,
                    title=f"Первый материал: {name}",
                    slug=f"{section.slug}-{slug}-intro",
                    summary=f"Вводный текст рубрики «{name}» раздела {section.name}.",
                    content=(
                        f"# {name}\n\n"
                        f"Это заготовка первого поста в рубрике **{name}**.\n\n"
                        f"Замени этот текст своим материалом — либо через админку/консоль, "
                        f"либо позже через Telegram-бота."
                    ),
                    author="SELF",
                    published=True,
                    published_at=datetime.utcnow(),
                )
                db.session.add(post)

    db.session.commit()
