from flask import Blueprint, render_template, abort, request

from models import Section, Subsection, Post

bp = Blueprint("sections", __name__)


@bp.route("/<section_slug>/")
def section_view(section_slug):
    section = Section.query.filter_by(slug=section_slug).first_or_404()

    tag_slug = request.args.get("tag")
    posts_query = (
        Post.query.join(Subsection)
        .filter(Subsection.section_id == section.id, Post.published.is_(True))
    )
    if tag_slug:
        posts_query = posts_query.filter(Post.tags.any(slug=tag_slug))

    posts = posts_query.order_by(Post.published_at.desc()).all()

    return render_template(
        "section.html", section=section, posts=posts, active_subsection=None, active_tag=tag_slug
    )


@bp.route("/<section_slug>/<subsection_slug>/")
def subsection_view(section_slug, subsection_slug):
    section = Section.query.filter_by(slug=section_slug).first_or_404()
    subsection = Subsection.query.filter_by(
        section_id=section.id, slug=subsection_slug
    ).first_or_404()

    posts = (
        Post.query.filter_by(subsection_id=subsection.id, published=True)
        .order_by(Post.published_at.desc())
        .all()
    )

    return render_template(
        "section.html", section=section, posts=posts, active_subsection=subsection, active_tag=None
    )


@bp.route("/post/<post_slug>/")
def post_view(post_slug):
    post = Post.query.filter_by(slug=post_slug, published=True).first_or_404()
    return render_template("post.html", post=post)
