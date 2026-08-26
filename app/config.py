import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RaktDaan Blood Bank Management System"
    SECRET_KEY: str = "raktdaan_super_secret_jwt_key_2026_secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./raktdaan.db"

    ADMIN_NAME: str = "System Admin"
    ADMIN_EMAIL: str = "admin@raktdaan.org"
    ADMIN_PASSWORD: str = "Admin@RaktDaan123"
    ADMIN_PHONE: str = "9876543210"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
