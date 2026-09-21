
# 📝 وبلاگ شخصی با Flask

یک وبلاگ کامل و حرفه‌ای با Flask — شامل CRUD پست‌ها، سیستم کامنت‌گذاری هوشمند، پنل ادمین و امکانات مدرن.

[![Tests](https://github.com/yasinsaffayy-max/flask-blog/actions/workflows/tests.yml/badge.svg)](https://github.com/yasinsaffayy-max/flask-blog/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ امکانات

### 📚 محتوا
- ✅ CRUD کامل پست‌ها (ایجاد، خواندن، ویرایش، حذف)
- ✅ دسته‌بندی پست‌ها
- ✅ Slug خودکار از عنوان
- ✅ ویرایشگر متن غنی (TinyMCE)
- ✅ آپلود تصویر شاخص برای هر پست
- ✅ زمان تقریبی مطالعه هر پست
- ✅ آمار بازدید یکتا (بر اساس IP)

### 💬 کامنت‌گذاری هوشمند
سه حالت برای هر پست:
- 🔴 غیرفعال — کامنت‌ها بسته
- 🟢 آزاد — کامنت‌ها فوری نمایش داده می‌شن
- 🟡 با تأیید — ادمین باید تأیید کنه

### 🎛 پنل ادمین
- ✅ داشبورد با آمار
- ✅ مدیریت پست‌ها، دسته‌ها، کامنت‌ها
- ✅ تأیید/رد کامنت‌ها
- ✅ انتشار/لغو انتشار پست‌ها

### 🎨 تجربه کاربری
- ✅ RSS Feed برای خوانندگان
- ✅ جستجوی زنده (AJAX)
- ✅ دکمه‌های اشتراک‌گذاری (تلگرام، X، واتساپ، لینکدین)
- ✅ حالت تاریک 🌙 (قابل تغییر)
- ✅ کاملاً رسپانسیو (موبایل + دسکتاپ)
- ✅ RTL کامل با فونت وزیرمتن

### 🔒 امنیت
- ✅ CSRF Protection روی همه فرم‌ها
- ✅ هش امن پسورد (werkzeug)
- ✅ Session امن
- ✅ Slug یکتا

## 🛠 تکنولوژی‌ها

| بخش | تکنولوژی |
|-----|----------|
| Backend | Flask 3, SQLAlchemy, Flask-Login, Flask-WTF |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Bootstrap 5 RTL, Bootstrap Icons, Vazirmatn |
| Editor | TinyMCE 6 |
| Deployment | Gunicorn, WhiteNoise |

## 🚀 نصب و اجرا

### پیش‌نیاز
- Python 3.10+

### مراحل

```bash
# 1. کلون پروژه
git clone https://github.com/yasinsaffayy-max/flask-blog.git
cd flask-blog

# 2. ساخت virtualenv
python -m venv venv
source venv/bin/activate  # ویندوز: venv\Scripts\activate

# 3. نصب پکیج‌ها
pip install -r requirements.txt

# 4. ساخت فایل .env
cp .env.example .env
# مقدار SECRET_KEY رو ویرایش کن

# 5. ساخت دیتابیس و داده اولیه
python init_db.py

# 6. اجرا
python run.py
```

مرورگر: http://127.0.0.1:5000

🔐 ورود ادمین

· URL: /auth/login
· Username: admin
· Password: admin123

⚠️ بعد از اولین ورود، رمز رو تغییر بده!

📁 ساختار پروژه

```
flask-blog/
├── app/
│   ├── __init__.py          # App Factory
│   ├── models.py            # User, Post, Category, Comment, PostView
│   ├── forms.py             # WTForms
│   ├── decorators.py        # admin_required
│   ├── routes/
│   │   ├── main.py          # صفحه اصلی، RSS، API جستجو
│   │   ├── auth.py          # ورود/خروج
│   │   ├── post.py          # جزئیات پست + کامنت
│   │   └── admin.py         # پنل ادمین
│   ├── templates/
│   └── static/
├── instance/                # دیتابیس SQLite
├── config.py
├── run.py
├── init_db.py
├── requirements.txt
├── Procfile
├── runtime.txt
└── README.md
```

📸 اسکرین‌شات‌ها

(به‌زودی اضافه میشه)

📝 لایسنس

MIT — هر کسی می‌تونه استفاده کنه.
