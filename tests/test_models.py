import pytest
from app.models import User, Category, Post, Comment, make_slug


class TestUser:
    def test_password_hashing(self, db):
        u = User(username='test', email='t@t.com')
        u.set_password('secret')
        assert u.password_hash != 'secret'
        assert u.check_password('secret')
        assert not u.check_password('wrong')

    def test_user_creation(self, user):
        assert user.id is not None
        assert user.username == 'ali'
        assert user.is_admin is False


class TestCategory:
    def test_creation(self, category):
        assert category.id is not None
        assert category.name == 'برنامه‌نویسی'
        assert category.slug == 'coding'


class TestPost:
    def test_creation(self, post):
        assert post.id is not None
        assert post.title == 'پست تست'
        assert post.is_published is True

    def test_reading_time(self, db, admin, category):
        # یه پست با ۴۰۰ کلمه بساز → باید ۲ دقیقه بشه
        body = ' '.join(['کلمه'] * 400)
        p = Post(
            title='t', slug='t', body=body,
            author_id=admin.id, category_id=category.id,
        )
        db.session.add(p)
        db.session.commit()
        assert p.reading_time == 2

    def test_reading_time_short_post(self, post):
        # پست کوتاه → حداقل ۱ دقیقه
        assert post.reading_time >= 1

    def test_can_comment_disabled(self, db, admin, category):
        p = Post(
            title='t', slug='t', body='b',
            author_id=admin.id, category_id=category.id,
            comment_mode=Post.COMMENT_DISABLED,
        )
        db.session.add(p)
        db.session.commit()
        assert p.can_comment() is False

    def test_can_comment_enabled(self, db, admin, category):
        p = Post(
            title='t', slug='t', body='b',
            author_id=admin.id, category_id=category.id,
            comment_mode=Post.COMMENT_ENABLED,
        )
        db.session.add(p)
        db.session.commit()
        assert p.can_comment() is True
        assert p.needs_approval() is False

    def test_needs_approval(self, post):
        assert post.needs_approval() is True

    def test_approved_comments_empty(self, post):
        assert post.approved_comments() == []

    def test_approved_comments_filters(self, db, post):
        c1 = Comment(body='ok', author_name='a', author_email='a@t.com',
                     post_id=post.id, is_approved=True)
        c2 = Comment(body='pending', author_name='b', author_email='b@t.com',
                     post_id=post.id, is_approved=False)
        db.session.add_all([c1, c2])
        db.session.commit()
        approved = post.approved_comments()
        assert len(approved) == 1
        assert approved[0].body == 'ok'


class TestSlugHelper:
    def test_make_slug_english(self):
        assert make_slug('Hello World') == 'hello-world'

    def test_make_slug_persian(self):
        result = make_slug('سلام دنیا')
        assert 'سلام' in result

    def test_make_slug_special_chars(self):
        result = make_slug('Hello! @#$ World?')
        assert '@' not in result
        assert '!' not in result

    def test_make_slug_max_length(self):
        long_text = 'a' * 500
        assert len(make_slug(long_text)) <= 200


class TestComment:
    def test_creation(self, db, post):
        c = Comment(
            body='نظر تست',
            author_name='علی',
            author_email='ali@test.com',
            post_id=post.id,
            is_approved=False,
        )
        db.session.add(c)
        db.session.commit()
        assert c.id is not None
        assert c.is_approved is False

    def test_cascade_delete(self, db, post):
        c1 = Comment(body='1', author_name='a', author_email='a@t.com', post_id=post.id)
        c2 = Comment(body='2', author_name='b', author_email='b@t.com', post_id=post.id)
        db.session.add_all([c1, c2])
        db.session.commit()
        assert Comment.query.count() == 2

        db.session.delete(post)
        db.session.commit()
        assert Comment.query.count() == 0
