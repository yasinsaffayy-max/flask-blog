from flask import Blueprint, render_template, request, jsonify, Response, url_for
from app.models import Post, Category

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '')

    query = Post.query.filter_by(is_published=True)
    if search:
        query = query.filter((Post.title.contains(search)) | (Post.body.contains(search)))
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6, error_out=False)
    categories = Category.query.all()

    return render_template('home.html', posts=posts, categories=categories,
                           search=search, current_category=category_slug, title='وبلاگ من')


@main_bp.route('/about')
def about():
    return render_template('about.html', title='درباره من')


@main_bp.route('/rss')
def rss():
    """فید RSS"""
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(20).all()

    items = ''
    for p in posts:
        link = url_for('post.detail', slug=p.slug, _external=True)
        desc = p.summary or (p.body[:200] if p.body else '')
        items += f'''
        <item>
            <title><![CDATA[{p.title}]]></title>
            <link>{link}</link>
            <guid>{link}</guid>
            <pubDate>{p.created_at.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
            <description><![CDATA[{desc}]]></description>
        </item>'''

    rss_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>وبلاگ من</title>
    <link>{url_for('main.home', _external=True)}</link>
    <description>وبلاگ شخصی یاسین صفایی</description>
    <language>fa</language>
    {items}
</channel>
</rss>'''

    return Response(rss_xml, mimetype='application/rss+xml')


@main_bp.route('/api/search')
def api_search():
    """جستجوی زنده - API"""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    posts = Post.query.filter(
        Post.is_published == True,
        (Post.title.contains(q)) | (Post.body.contains(q))
    ).order_by(Post.created_at.desc()).limit(6).all()

    return jsonify([{
        'title': p.title,
        'slug': p.slug,
        'summary': (p.summary or p.body[:80]) if p.summary or p.body else '',
        'url': url_for('post.detail', slug=p.slug)
    } for p in posts])
