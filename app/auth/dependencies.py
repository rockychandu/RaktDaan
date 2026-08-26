from functools import wraps
from flask import request, jsonify, g
from app.database.connection import db
from app.database.models.user import User
from app.users.models import UserRole
from app.security.jwt_manager import JWTManager
from app.security.rbac_matrix import RBACPermissionMatrix

def get_current_user() -> User:
    """
    Extracts Bearer token from Authorization header, verifies signature & revocation,
    and returns User model instance from database.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    payload = JWTManager.decode_and_verify(token, expected_type="access")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.session.get(User, int(user_id))
    if not user or user.is_deleted or user.status != "ACTIVE":
        return None

    g.token_payload = payload
    return user

def require_login(f):
    """Decorator ensuring request is made by an authenticated user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Authentication token required or invalid.", "detail": "Authentication token required or invalid."}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_donor(f):
    """Decorator enforcing that authenticated user has DONOR role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Authentication token required.", "detail": "Authentication token required."}), 401
        if user.role != UserRole.DONOR.value:
            return jsonify({"success": False, "message": "Access restricted to registered Donors only.", "detail": "Access restricted to registered Donors only."}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator enforcing that authenticated user has ADMIN role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Authentication token required.", "detail": "Authentication token required."}), 401
        if user.role != UserRole.ADMIN.value:
            return jsonify({"success": False, "message": "Access restricted to System Administrators only.", "detail": "Access restricted to System Administrators only."}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission: str):
    """Decorator enforcing granular RBAC permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"success": False, "message": "Authentication token required.", "detail": "Authentication token required."}), 401
            if not RBACPermissionMatrix.has_permission(user.role, permission):
                return jsonify({"success": False, "message": f"Insufficient permissions. Requires: {permission}", "detail": f"Insufficient permissions. Requires: {permission}"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
