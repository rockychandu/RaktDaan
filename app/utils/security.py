import jwt
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import Config

def hash_password(password: str) -> str:
    """
    Hashes a plain text password securely using scrypt/pbkdf2.
    Never store plain-text passwords in database.
    """
    return generate_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored secure password hash.
    """
    if not plain_password or not hashed_password:
        return False
    return check_password_hash(hashed_password, plain_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Generates a secure JWT access token with payload data (sub, role, email) and expiration.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now
    })
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT access token signature and expiration.
    Returns payload dictionary or None if invalid.
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
