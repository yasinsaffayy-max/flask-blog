import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    from app.models import User, Post, Category, Comment
    return {'db': db, 'User': User, 'Post': Post, 'Category': Category, 'Comment': Comment}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
