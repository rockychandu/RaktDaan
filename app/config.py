import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Enterprise Application Configuration for RaktDaan Blood Bank Management System.
    Loads settings from environment variables with secure defaults.
    """
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "RaktDaan Enterprise Blood Bank System")
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "raktdaan_super_secret_jwt_key_2026_enterprise_secure")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "v7ZgR8xM3qT6yW9aB1cD4eF7gH0iJ2kL3mN5oP8qR1s=")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    ACCOUNT_LOCKOUT_MINUTES: int = int(os.getenv("ACCOUNT_LOCKOUT_MINUTES", "15"))

    # Password Policy Configuration
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL_CHAR: bool = True
    PASSWORD_HISTORY_LIMIT: int = 3

    # Database Configuration
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///./raktdaan.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Initial Default System Admin Setup
    ADMIN_NAME: str = os.getenv("ADMIN_NAME", "System Admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@raktdaan.org")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "RaktDaan@123")
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "9876543210")

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT_REQUESTS: int = 100
    DEFAULT_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: list = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "testing_secret_key"
    ENCRYPTION_KEY = "testing_encryption_key_32_bytes_long_string="
    RATE_LIMIT_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Enforce strict secret key requirement in production
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
