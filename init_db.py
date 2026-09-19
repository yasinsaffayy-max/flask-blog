"""ساخت دیتابیس و داده اولیه"""
from app import create_app, db
from app.models import User, Category, Post

app = create_app('development')

with app.app_context():
    db.create_all()
    print("✅ جداول ساخته شدند")

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@blog.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ ادمین ساخته شد (admin / admin123)")

    if Category.query.count() == 0:
        for name, slug in [('برنامه‌نویسی', 'coding'), ('لینوکس', 'linux'), ('شبکه', 'network')]:
            db.session.add(Category(name=name, slug=slug))
        db.session.commit()
        print("✅ ۳ دسته ساخته شد")

    if Post.query.count() == 0:
        admin = User.query.filter_by(username='admin').first()
        cat = Category.query.filter_by(slug='coding').first()
        post = Post(
            title='اولین پست من',
            slug='first-post',
            summary='این اولین پست وبلاگ منه',
            body='سلام! این اولین پست وبلاگ منه. اینجا از تجربه‌هام می‌نویسم.',
            author_id=admin.id,
            category_id=cat.id,
            is_published=True,
            comment_mode='approval'
        )
        db.session.add(post)
        db.session.commit()
        print("✅ اولین پست ساخته شد")

    print("\n🎉 آماده‌ست! حالا `python run.py` بزن.")
