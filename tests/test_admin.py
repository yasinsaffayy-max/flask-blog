from app.models import Post, Category, Comment


class TestAdminAccess:
    def test_dashboard_requires_login(self, client):
        r = client.get('/admin/')
        assert r.status_code == 302

    def test_dashboard_requires_admin(self, auth_client):
        r = auth_client.get('/admin/')
        assert r.status_code == 403

    def test_dashboard_admin_ok(self, admin_client):
        r = admin_client.get('/admin/')
        assert r.status_code == 200


class TestPostManagement:
    def test_list_posts(self, admin_client, post):
        r = admin_client.get('/admin/posts')
        assert r.status_code == 200

    def test_new_post_form(self, admin_client):
        r = admin_client.get('/admin/posts/new')
        assert r.status_code == 200

    def test_create_post(self, admin_client, db, category):
        r = admin_client.post('/admin/posts/new', data={
            'title': 'پست جدید',
            'slug': 'new-post',
            'summary': 'خلاصه',
            'body': 'محتوا',
            'category_id': category.id,
            'comment_mode': 'approval',
            'is_published': True,
        }, follow_redirects=True)
        assert r.status_code == 200
        assert Post.query.filter_by(slug='new-post').first() is not None

    def test_create_post_auto_slug(self, admin_client, db, category):
        """اگه slug خالی باشه، خودکار ساخته بشه"""
        admin_client.post('/admin/posts/new', data={
            'title': 'Test Title',
            'slug': '',
            'body': 'content',
            'category_id': category.id,
            'comment_mode': 'approval',
            'is_published': True,
        }, follow_redirects=True)
        p = Post.query.filter_by(title='Test Title').first()
        assert p is not None
        assert p.slug != ''

    def test_edit_post(self, admin_client, db, post):
        r = admin_client.post(f'/admin/posts/{post.id}/edit', data={
            'title': 'عنوان ویرایش',
            'slug': post.slug,
            'summary': post.summary,
            'body': post.body,
            'category_id': post.category_id,
            'comment_mode': post.comment_mode,
            'is_published': True,
        }, follow_redirects=True)
        assert r.status_code == 200
        db.session.refresh(post)
        assert post.title == 'عنوان ویرایش'

    def test_delete_post(self, admin_client, db, post):
        r = admin_client.post(f'/admin/posts/{post.id}/delete', follow_redirects=True)
        assert Post.query.count() == 0

    def test_toggle_publish(self, admin_client, db, post):
        assert post.is_published is True
        admin_client.get(f'/admin/posts/{post.id}/toggle')
        db.session.refresh(post)
        assert post.is_published is False


class TestCategoryManagement:
    def test_list(self, admin_client, category):
        r = admin_client.get('/admin/categories')
        assert r.status_code == 200

    def test_create(self, admin_client, db):
        r = admin_client.post('/admin/categories', data={
            'name': 'لینوکس',
            'slug': 'linux',
        }, follow_redirects=True)
        assert Category.query.filter_by(slug='linux').first() is not None

    def test_duplicate_slug_rejected(self, admin_client, db, category):
        admin_client.post('/admin/categories', data={
            'name': 'تکراری',
            'slug': 'coding',
        }, follow_redirects=True)
        assert Category.query.filter_by(slug='coding').count() == 1


class TestCommentModeration:
    def test_list_comments(self, admin_client, post, db):
        c = Comment(body='ok', author_name='a', author_email='a@t.com', post_id=post.id)
        db.session.add(c)
        db.session.commit()
        r = admin_client.get('/admin/comments')
        assert r.status_code == 200

    def test_approve_comment(self, admin_client, db, post):
        c = Comment(body='ok', author_name='a', author_email='a@t.com',
                    post_id=post.id, is_approved=False)
        db.session.add(c)
        db.session.commit()
        admin_client.post(f'/admin/comments/{c.id}/approve')
        db.session.refresh(c)
        assert c.is_approved is True

    def test_reject_comment(self, admin_client, db, post):
        c = Comment(body='ok', author_name='a', author_email='a@t.com',
                    post_id=post.id, is_approved=True)
        db.session.add(c)
        db.session.commit()
        admin_client.post(f'/admin/comments/{c.id}/reject')
        db.session.refresh(c)
        assert c.is_approved is False

    def test_delete_comment(self, admin_client, db, post):
        c = Comment(body='ok', author_name='a', author_email='a@t.com', post_id=post.id)
        db.session.add(c)
        db.session.commit()
        admin_client.post(f'/admin/comments/{c.id}/delete')
        assert Comment.query.count() == 0
