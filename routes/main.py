from flask import Blueprint, render_template

from extensions import db
from models import Section, Post

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    sections = Section.query.order_by(Section.order).all()

    recent_posts = (
        Post.query.filter_by(published=True)
        .order_by(Post.published_at.desc())
        .limit(6)
        .all()
    )
    return render_template("index.html", sections=sections, recent_posts=recent_posts)


@bp.route("/about")
def about():
    return render_template("about.html")
