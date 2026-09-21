import os
import tempfile
import pytest
from app import create_app, db as _db
from app.models import User, Category, Post, Comment


UPLOAD_TMP = os.path.join(tempfile.gettempdir(), 'blog_uploads_test')
os.makedirs(UPLOAD_TMP, exist_ok=True)


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-blog'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_TMP
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


@pytest.fixture(scope='session')
def app():
    from config import config
    config['test'] = TestConfig
    app = create_app('test')
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def user(db):
    u = User(username='ali', email='ali@test.com')
    u.set_password('password123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def admin(db):
    u = User(username='admin', email='admin@test.com', is_admin=True)
    u.set_password('admin123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def category(db):
    c = Category(name='برنامه‌نویسی', slug='coding')
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture
def post(db, admin, category):
    p = Post(
        title='پست تست',
        slug='test-post',
        summary='خلاصه تست',
        body='محتوای پست تست',
        author_id=admin.id,
        category_id=category.id,
        is_published=True,
        comment_mode=Post.COMMENT_APPROVAL,
    )
    db.session.add(p)
    db.session.commit()
    return p


@pytest.fixture
def auth_client(client, user):
    client.post('/auth/login', data={
        'username': 'ali',
        'password': 'password123',
    }, follow_redirects=True)
    return client


@pytest.fixture
def admin_client(client, admin):
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123',
    }, follow_redirects=True)
    return client
