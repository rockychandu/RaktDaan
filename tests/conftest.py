import pytest
from app.main import create_app
from app.config import Config
from app.database.connection import db
from app.database.seed import seed_initial_admin

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test_secret_key"

@pytest.fixture(scope="function")
def app():
    """
    Creates and configures a new Flask app instance for each test.
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        seed_initial_admin()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """
    Flask test client for making API requests.
    """
    return app.test_client()
