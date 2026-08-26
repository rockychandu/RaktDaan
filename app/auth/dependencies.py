from functools import wraps
from flask import request, jsonify
from app.database.connection import db
from app.database.models import User
from app.users.models import UserRole
from app.utils.security import decode_access_token

def get_current_user() -> User:
    """
    Extracts Bearer token from Authorization header, decodes JWT, and returns User model from DB.
    Returns None if missing or invalid.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Use db.session.get for SQLAlchemy 2.0 compatibility
    user = db.session.get(User, int(user_id))
    if not user or user.status != "ACTIVE":
        return None

    return user

def require_login(f):
    """
    Decorator requiring an authenticated user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Authentication token required or invalid."}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_donor(f):
    """
    Decorator enforcing that logged in user has DONOR role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Authentication token required."}), 401
        if user.role != UserRole.DONOR.value:
            return jsonify({"detail": "Access restricted to registered Donors only."}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """
    Decorator enforcing that logged in user has ADMIN role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Authentication token required."}), 401
        if user.role != UserRole.ADMIN.value:
            return jsonify({"detail": "Access restricted to System Administrators only."}), 403
        return f(*args, **kwargs)
    return decorated_function
