from flask import Blueprint, request, jsonify
from app.users.models import UserRole
from app.utils.security import create_access_token
from app.auth.validators import validate_donor_registration, validate_login_request, ValidationError
from app.auth.services import register_donor_service, authenticate_user_service
from app.auth.dependencies import require_login, require_donor, require_admin, get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/register", methods=["POST"])
def register_donor():
    """
    Public Donor Registration Endpoint.
    Validates input fields, checks email uniqueness, hashes password, creates donor profile.
    """
    data = request.get_json(silent=True) or {}
    try:
        cleaned_data = validate_donor_registration(data)
        user = register_donor_service(cleaned_data)
        return jsonify(user.to_dict()), 201
    except ValidationError as ve:
        return jsonify({"detail": ve.errors}), 422


@auth_bp.route("/donor/login", methods=["POST"])
def donor_login():
    """
    Donor Login Endpoint.
    Verifies credentials and ensures account has DONOR role before generating token.
    """
    data = request.get_json(silent=True) or {}
    try:
        email, password = validate_login_request(data)
    except ValidationError as ve:
        return jsonify({"detail": ve.errors}), 422

    user, error_msg, status_code = authenticate_user_service(email, password, expected_role=UserRole.DONOR.value)
    if error_msg:
        return jsonify({"detail": error_msg}), status_code

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "email": user.email
    }
    access_token = create_access_token(data=token_data)

    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """
    Admin Login Endpoint.
    Verifies credentials and ensures account has ADMIN role.
    Rejects normal donor accounts attempting admin login.
    """
    data = request.get_json(silent=True) or {}
    try:
        email, password = validate_login_request(data)
    except ValidationError as ve:
        return jsonify({"detail": ve.errors}), 422

    user, error_msg, status_code = authenticate_user_service(email, password, expected_role=UserRole.ADMIN.value)
    if error_msg:
        return jsonify({"detail": error_msg}), status_code

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "email": user.email
    }
    access_token = create_access_token(data=token_data)

    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@require_login
def logout():
    """
    Logout Endpoint.
    Informs client to discard session/token.
    """
    user = get_current_user()
    return jsonify({
        "success": True,
        "message": f"Successfully logged out user {user.email}."
    }), 200


@auth_bp.route("/me", methods=["GET"])
@require_login
def get_current_user_profile():
    """
    Get current logged in user profile (Donor or Admin).
    Requires valid authentication token. Excludes sensitive password_hash.
    """
    user = get_current_user()
    return jsonify(user.to_dict()), 200


@auth_bp.route("/donor/dashboard-data", methods=["GET"])
@require_donor
def donor_dashboard_sample():
    """
    Protected Donor-only route test. Returns donor details.
    """
    user = get_current_user()
    return jsonify({
        "message": f"Welcome to Donor Dashboard, {user.name}!",
        "donor_id": user.donor_profile.id if user.donor_profile else None,
        "blood_group": user.donor_profile.blood_group if user.donor_profile else None
    }), 200


@auth_bp.route("/admin/dashboard-data", methods=["GET"])
@require_admin
def admin_dashboard_sample():
    """
    Protected Admin-only route test. Returns admin details.
    """
    user = get_current_user()
    return jsonify({
        "message": f"Welcome to Admin Dashboard, {user.name}!",
        "admin_email": user.email
    }), 200
