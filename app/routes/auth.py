from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('نام کاربری یا رمز عبور اشتباه است.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        flash(f'خوش آمدی {user.username}!', 'success')

        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))

    return render_template('auth/login.html', form=form, title='ورود')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('با موفقیت خارج شدی.', 'info')
    return redirect(url_for('main.home'))
