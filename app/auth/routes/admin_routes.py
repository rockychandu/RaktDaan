from flask import Blueprint, request, jsonify
from app.users.models import UserRole
from app.users.exceptions import DomainException
from app.auth.validators.login_validator import LoginValidator
from app.auth.services.authentication_service import AuthenticationService
from app.auth.dependencies import require_admin, get_current_user
from app.security.rate_limiter import SlidingWindowRateLimiter
from app.utils.response_builder import ApiResponse

admin_bp = Blueprint("admin_auth", __name__, url_prefix="/api/v1/auth")

@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """
    Admin Login Endpoint.
    Verifies credentials and ensures account has ADMIN role.
    Rejects normal donor accounts attempting admin login.
    """
    ip_addr = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    is_limited, _ = SlidingWindowRateLimiter.is_rate_limited(f"admin_login_{ip_addr}", max_requests=5, window_seconds=60)
    if is_limited:
        return ApiResponse.error("Too many admin login attempts. Account protection active.", status_code=429)

    data = request.get_json(silent=True) or {}
    try:
        email, password = LoginValidator.validate(data)
        auth_result = AuthenticationService.authenticate_user(
            email=email,
            password=password,
            expected_role=UserRole.ADMIN.value,
            ip_address=ip_addr,
            user_agent=user_agent
        )
        response_payload = {
            "access_token": auth_result["tokens"]["access_token"],
            "refresh_token": auth_result["tokens"]["refresh_token"],
            "token_type": auth_result["tokens"]["token_type"],
            "role": auth_result["tokens"]["role"],
            "user": auth_result["user"].to_dict()
        }
        return jsonify(response_payload), 200
    except DomainException as de:
        return ApiResponse.error(message=de.message, status_code=de.status_code, errors=de.errors)


@admin_bp.route("/admin/dashboard-data", methods=["GET"])
@require_admin
def admin_dashboard_sample():
    """
    Protected Admin-only route test.
    """
    user = get_current_user()
    return jsonify({
        "message": f"Welcome to Admin Dashboard, {user.name}!",
        "admin_email": user.email
    }), 200
