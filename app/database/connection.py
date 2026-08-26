from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """
    Initialize SQLAlchemy database extension with Flask application.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
