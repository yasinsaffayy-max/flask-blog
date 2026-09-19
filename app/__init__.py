from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'لطفاً ابتدا وارد شوید.'
    login_manager.login_message_category = 'warning'

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.post import post_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(post_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('main.home'))

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, int(user_id))
