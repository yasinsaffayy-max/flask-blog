from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, SelectField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Optional
)
from app.models import User, Post, Category


class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    remember = BooleanField('مرا به خاطر بسپار')
    submit = SubmitField('ورود')


class PostForm(FlaskForm):
    title = StringField('عنوان', validators=[DataRequired(), Length(3, 200)])
    slug = StringField('نامک (slug)', validators=[Optional(), Length(0, 200)])
    summary = StringField('خلاصه', validators=[Optional(), Length(0, 300)])
    body = TextAreaField('متن پست', validators=[DataRequired()])
    category_id = SelectField('دسته‌بندی', coerce=int, validators=[Optional()])
    comment_mode = SelectField('حالت کامنت‌ها', choices=[
        (Post.COMMENT_DISABLED, 'غیرفعال'),
        (Post.COMMENT_ENABLED, 'آزاد (بدون تأیید)'),
        (Post.COMMENT_APPROVAL, 'با تأیید ادمین'),
    ], default=Post.COMMENT_APPROVAL)
    image = FileField('تصویر شاخص', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'فقط تصویر مجاز است!')
    ])
    is_published = BooleanField('منتشر شده', default=True)
    submit = SubmitField('ذخیره')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = [(0, '--- بدون دسته ---')] + [
            (c.id, c.name) for c in Category.query.all()
        ]


class CategoryForm(FlaskForm):
    name = StringField('نام دسته', validators=[DataRequired(), Length(2, 100)])
    slug = StringField('نامک', validators=[DataRequired(), Length(2, 100)])
    submit = SubmitField('ذخیره')


class CommentForm(FlaskForm):
    author_name = StringField('نام شما', validators=[DataRequired(), Length(2, 100)])
    author_email = StringField('ایمیل', validators=[DataRequired(), Email(message='ایمیل معتبر نیست.')])
    body = TextAreaField('متن نظر', validators=[DataRequired(), Length(3, 2000)])
    submit = SubmitField('ارسال نظر')
