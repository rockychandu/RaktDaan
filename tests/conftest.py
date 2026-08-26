import pytest
from app.main import create_app
from app.config import TestingConfig
from app.database.connection import db
from app.database.seed import seed_all
from app.security.rate_limiter import SlidingWindowRateLimiter

@pytest.fixture(scope="function")
def app():
    """
    Creates and configures a fresh Flask app instance for testing.
    """
    app = create_app(TestingConfig)
    SlidingWindowRateLimiter.reset()
    with app.app_context():
        db.create_all()
        seed_all()
        yield app
        db.session.remove()
        db.drop_all()
    SlidingWindowRateLimiter.reset()

@pytest.fixture(scope="function")
def client(app):
    """
    Flask test client for making API requests.
    """
    return app.test_client()
