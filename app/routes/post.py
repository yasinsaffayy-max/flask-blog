import os
import uuid
from hashlib import sha256
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    current_app, abort
)
from flask_login import current_user
from app import db
from app.models import Post, Comment, PostView
from app.forms import CommentForm

post_bp = Blueprint('post', __name__)


def save_image(file):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename


def delete_image(filename):
    if not filename:
        return
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)


def record_view(post):
    """ثبت بازدید یکتا"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '0.0.0.0'
    ip = ip.split(',')[0].strip()
    ip_hash = sha256((ip + current_app.config['SECRET_KEY']).encode()).hexdigest()[:32]

    exists = PostView.query.filter_by(post_id=post.id, ip_hash=ip_hash).first()
    if not exists:
        db.session.add(PostView(post_id=post.id, ip_hash=ip_hash))
        post.views = (post.views or 0) + 1
        db.session.commit()


@post_bp.route('/post/<slug>', methods=['GET', 'POST'])
def detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()

    if not post.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        abort(404)

    record_view(post)

    form = CommentForm()
    if form.validate_on_submit():
        if not post.can_comment():
            flash('کامنت‌های این پست غیرفعال است.', 'warning')
            return redirect(url_for('post.detail', slug=post.slug))

        comment = Comment(
            body=form.body.data,
            author_name=form.author_name.data,
            author_email=form.author_email.data,
            post_id=post.id,
            is_approved=not post.needs_approval()
        )
        db.session.add(comment)
        db.session.commit()

        if post.needs_approval():
            flash('نظر شما ثبت شد و پس از تأیید نمایش داده می‌شود.', 'info')
        else:
            flash('نظر شما ثبت شد.', 'success')

        return redirect(url_for('post.detail', slug=post.slug))

    related = []
    if post.category_id:
        related = Post.query.filter(
            Post.category_id == post.category_id,
            Post.id != post.id,
            Post.is_published == True
        ).limit(3).all()

    return render_template('post/detail.html', post=post, form=form, related=related, title=post.title)
