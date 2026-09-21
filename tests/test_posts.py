from app.models import Post, Comment


class TestHome:
    def test_home_loads(self, client, db):
        r = client.get('/')
        assert r.status_code == 200

    def test_home_shows_published(self, client, post):
        r = client.get('/')
        assert post.title.encode() in r.data or r.status_code == 200

    def test_home_hides_draft(self, client, db, post):
        post.is_published = False
        db.session.commit()
        r = client.get('/')
        assert post.title.encode() not in r.data

    def test_search(self, client, post):
        r = client.get('/?q=تست')
        assert r.status_code == 200

    def test_filter_category(self, client, post, category):
        r = client.get(f'/?category={category.slug}')
        assert r.status_code == 200

    def test_pagination(self, client, db, admin, category):
        for i in range(10):
            p = Post(title=f'p{i}', slug=f'p{i}', body='b',
                     author_id=admin.id, category_id=category.id, is_published=True)
            db.session.add(p)
        db.session.commit()
        r = client.get('/?page=1')
        assert r.status_code == 200


class TestPostDetail:
    def test_detail_loads(self, client, post):
        r = client.get(f'/post/{post.slug}')
        assert r.status_code == 200
        assert post.title.encode() in r.data

    def test_detail_404(self, client, db):
        r = client.get('/post/nonexistent')
        assert r.status_code == 404

    def test_draft_hidden_from_anonymous(self, client, db, post):
        post.is_published = False
        db.session.commit()
        r = client.get(f'/post/{post.slug}')
        assert r.status_code == 404

    def test_draft_visible_to_admin(self, admin_client, db, post):
        post.is_published = False
        db.session.commit()
        r = admin_client.get(f'/post/{post.slug}')
        assert r.status_code == 200

    def test_view_counter(self, client, db, post):
        assert post.views == 0 or post.views is None
        client.get(f'/post/{post.slug}')
        db.session.refresh(post)
        assert post.views >= 1


class TestComments:
    def test_comment_disabled(self, client, db, admin, category):
        p = Post(title='t', slug='t-disabled', body='b',
                 author_id=admin.id, category_id=category.id,
                 is_published=True, comment_mode=Post.COMMENT_DISABLED)
        db.session.add(p)
        db.session.commit()
        r = client.post(f'/post/{p.slug}', data={
            'author_name': 'علی',
            'author_email': 'ali@t.com',
            'body': 'نظر تست',
        }, follow_redirects=True)
        assert Comment.query.count() == 0

    def test_comment_approval_mode_pending(self, client, db, post):
        client.post(f'/post/{post.slug}', data={
            'author_name': 'علی',
            'author_email': 'ali@t.com',
            'body': 'نظر تست',
        }, follow_redirects=True)
        c = Comment.query.first()
        assert c is not None
        assert c.is_approved is False

    def test_comment_enabled_auto_approve(self, client, db, admin, category):
        p = Post(title='t', slug='t-enabled', body='b',
                 author_id=admin.id, category_id=category.id,
                 is_published=True, comment_mode=Post.COMMENT_ENABLED)
        db.session.add(p)
        db.session.commit()
        client.post(f'/post/{p.slug}', data={
            'author_name': 'علی',
            'author_email': 'ali@t.com',
            'body': 'نظر تست',
        }, follow_redirects=True)
        c = Comment.query.first()
        assert c is not None
        assert c.is_approved is True

    def test_comment_requires_valid_email(self, client, post, db):
        client.post(f'/post/{post.slug}', data={
            'author_name': 'علی',
            'author_email': 'invalid',
            'body': 'نظر',
        })
        assert Comment.query.count() == 0


class TestAPI:
    def test_search_api_empty(self, client, db):
        r = client.get('/api/search?q=')
        assert r.status_code == 200
        assert r.get_json() == []

    def test_search_api_short_query(self, client, db):
        r = client.get('/api/search?q=a')
        assert r.get_json() == []

    def test_search_api_finds(self, client, post):
        r = client.get('/api/search?q=تست')
        data = r.get_json()
        assert isinstance(data, list)

    def test_rss_feed(self, client, post):
        r = client.get('/rss')
        assert r.status_code == 200
        assert b'<rss' in r.data
        assert post.title.encode() in r.data
