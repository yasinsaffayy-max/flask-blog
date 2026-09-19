import re
import math
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


def make_slug(text):
    """ساخت slug از متن (فارسی و انگلیسی)"""
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-\u0600-\u06FF]', '', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:200]


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    posts = db.relationship('Post', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Post(db.Model):
    __tablename__ = 'posts'
    COMMENT_DISABLED = 'disabled'
    COMMENT_ENABLED = 'enabled'
    COMMENT_APPROVAL = 'approval'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(300))
    body = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=True)
    comment_mode = db.Column(db.String(20), default=COMMENT_APPROVAL)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    views_rel = db.relationship('PostView', backref='post', lazy=True, cascade='all, delete-orphan')

    def can_comment(self):
        return self.comment_mode != self.COMMENT_DISABLED

    def needs_approval(self):
        return self.comment_mode == self.COMMENT_APPROVAL

    def approved_comments(self):
        return [c for c in self.comments if c.is_approved]

    @property
    def reading_time(self):
        """زمان تقریبی مطالعه به دقیقه"""
        words = len(self.body.split()) if self.body else 0
        return max(1, math.ceil(words / 200))

    def __repr__(self):
        return f'<Post {self.title}>'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'


class PostView(db.Model):
    """بازدید یکتای هر پست بر اساس IP"""
    __tablename__ = 'post_views'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    ip_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'ip_hash', name='uq_post_ip'),)
