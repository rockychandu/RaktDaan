import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "RaktDaan Blood Bank Management System")
    SECRET_KEY = os.getenv("SECRET_KEY", "raktdaan_super_secret_jwt_key_2026_secure")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///./raktdaan.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seed Admin Config
    ADMIN_NAME = os.getenv("ADMIN_NAME", "System Admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@raktdaan.org")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@RaktDaan123")
    ADMIN_PHONE = os.getenv("ADMIN_PHONE", "9876543210")
