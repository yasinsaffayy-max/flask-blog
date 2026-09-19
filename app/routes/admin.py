from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app import db
from app.models import Post, Category, Comment, User, make_slug
from app.forms import PostForm, CategoryForm
from app.decorators import admin_required
from app.routes.post import save_image, delete_image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def unique_slug(base, current_id=None):
    """ساخت slug یکتا"""
    slug = base
    counter = 1
    while True:
        q = Post.query.filter_by(slug=slug)
        if current_id:
            q = q.filter(Post.id != current_id)
        if not q.first():
            return slug
        slug = f"{base}-{counter}"
        counter += 1


@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'posts': Post.query.count(),
        'published': Post.query.filter_by(is_published=True).count(),
        'categories': Category.query.count(),
        'comments': Comment.query.count(),
        'pending_comments': Comment.query.filter_by(is_approved=False).count(),
    }
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_posts=recent_posts, title='داشبورد ادمین')


@admin_bp.route('/posts')
@admin_required
def posts():
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=all_posts, title='مدیریت پست‌ها')


@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@admin_required
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        image_name = save_image(form.image.data)
        raw_slug = form.slug.data or make_slug(form.title.data)
        post = Post(
            title=form.title.data,
            slug=unique_slug(raw_slug),
            summary=form.summary.data,
            body=form.body.data,
            category_id=form.category_id.data or None,
            comment_mode=form.comment_mode.data,
            image=image_name,
            is_published=form.is_published.data,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash(f'پست «{post.title}» ساخته شد.', 'success')
        return redirect(url_for('admin.posts'))
    return render_template('admin/post_form.html', form=form, title='پست جدید')


@admin_bp.route('/posts/<int:pid>/edit', methods=['GET', 'POST'])
@admin_required
def post_edit(pid):
    post = Post.query.get_or_404(pid)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data
        raw_slug = form.slug.data or make_slug(form.title.data)
        post.slug = unique_slug(raw_slug, current_id=post.id)
        post.summary = form.summary.data
        post.body = form.body.data
        post.category_id = form.category_id.data or None
        post.comment_mode = form.comment_mode.data
        post.is_published = form.is_published.data

        if form.image.data and form.image.data.filename:
            delete_image(post.image)
            post.image = save_image(form.image.data)

        db.session.commit()
        flash('پست ویرایش شد.', 'success')
        return redirect(url_for('admin.posts'))

    return render_template('admin/post_form.html', form=form, post=post, title='ویرایش پست')


@admin_bp.route('/posts/<int:pid>/delete', methods=['POST'])
@admin_required
def post_delete(pid):
    post = Post.query.get_or_404(pid)
    delete_image(post.image)
    db.session.delete(post)
    db.session.commit()
    flash('پست حذف شد.', 'info')
    return redirect(url_for('admin.posts'))


@admin_bp.route('/posts/<int:pid>/toggle')
@admin_required
def post_toggle(pid):
    post = Post.query.get_or_404(pid)
    post.is_published = not post.is_published
    db.session.commit()
    state = 'منتشر شد' if post.is_published else 'از انتشار درآمد'
    flash(f'پست {state}.', 'info')
    return redirect(url_for('admin.posts'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(slug=form.slug.data).first():
            flash('این slug قبلاً استفاده شده.', 'danger')
        else:
            db.session.add(Category(name=form.name.data, slug=form.slug.data))
            db.session.commit()
            flash('دسته اضافه شد.', 'success')
        return redirect(url_for('admin.categories'))
    all_cats = Category.query.all()
    return render_template('admin/categories.html', categories=all_cats, form=form, title='دسته‌بندی‌ها')


@admin_bp.route('/categories/<int:cid>/delete', methods=['POST'])
@admin_required
def category_delete(cid):
    cat = Category.query.get_or_404(cid)
    db.session.delete(cat)
    db.session.commit()
    flash('دسته حذف شد.', 'info')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/comments')
@admin_required
def comments():
    status = request.args.get('status', '')
    query = Comment.query
    if status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'approved':
        query = query.filter_by(is_approved=True)
    all_comments = query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=all_comments, status_filter=status, title='مدیریت کامنت‌ها')


@admin_bp.route('/comments/<int:cid>/approve', methods=['POST'])
@admin_required
def comment_approve(cid):
    comment = Comment.query.get_or_404(cid)
    comment.is_approved = True
    db.session.commit()
    flash('کامنت تأیید شد.', 'success')
    return redirect(request.referrer or url_for('admin.comments'))


@admin_bp.route('/comments/<int:cid>/reject', methods=['POST'])
@admin_required
def comment_reject(cid):
    comment = Comment.query.get_or_404(cid)
    comment.is_approved = False
    db.session.commit()
    flash('کامنت رد شد.', 'info')
    return redirect(request.referrer or url_for('admin.comments'))


@admin_bp.route('/comments/<int:cid>/delete', methods=['POST'])
@admin_required
def comment_delete(cid):
    comment = Comment.query.get_or_404(cid)
    db.session.delete(comment)
    db.session.commit()
    flash('کامنت حذف شد.', 'info')
    return redirect(request.referrer or url_for('admin.comments'))
