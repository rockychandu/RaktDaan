from flask import Blueprint, request, jsonify, g
from app.users.models import UserRole
from app.users.exceptions import DomainException
from app.auth.validators.registration_validator import RegistrationValidator
from app.auth.validators.login_validator import LoginValidator
from app.auth.services.registration_service import RegistrationService
from app.auth.services.authentication_service import AuthenticationService
from app.auth.services.token_service import TokenService
from app.auth.dependencies import require_login, require_donor, get_current_user
from app.security.rate_limiter import SlidingWindowRateLimiter
from app.utils.response_builder import ApiResponse

donor_bp = Blueprint("donor_auth", __name__, url_prefix="/api/v1/auth")

@donor_bp.route("/register", methods=["POST"])
def register_donor():
    """
    Public Donor Registration Endpoint.
    Validates 12 fields, checks email uniqueness, hashes password, creates profile.
    """
    ip_addr = request.remote_addr
    is_limited, _ = SlidingWindowRateLimiter.is_rate_limited(f"reg_{ip_addr}", max_requests=10, window_seconds=60)
    if is_limited:
        return ApiResponse.error("Too many registration requests. Please wait a minute.", status_code=429)

    data = request.get_json(silent=True) or {}
    try:
        validated_data = RegistrationValidator.validate(data)
        user = RegistrationService.register_donor(validated_data, ip_address=ip_addr)
        return ApiResponse.success(data=user.to_dict(), message="Donor registered successfully.", status_code=201)
    except DomainException as de:
        return ApiResponse.error(message=de.message, status_code=de.status_code, errors=de.errors)


@donor_bp.route("/donor/login", methods=["POST"])
def donor_login():
    """
    Donor Login Endpoint.
    Verifies credentials and ensures account has DONOR role before generating token.
    """
    ip_addr = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    is_limited, _ = SlidingWindowRateLimiter.is_rate_limited(f"login_{ip_addr}", max_requests=15, window_seconds=60)
    if is_limited:
        return ApiResponse.error("Too many login attempts. Please wait a minute.", status_code=429)

    data = request.get_json(silent=True) or {}
    try:
        email, password = LoginValidator.validate(data)
        auth_result = AuthenticationService.authenticate_user(
            email=email,
            password=password,
            expected_role=UserRole.DONOR.value,
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


@donor_bp.route("/logout", methods=["POST"])
@require_login
def logout():
    """
    Logout Endpoint.
    Revokes current user session token.
    """
    user = get_current_user()
    token_payload = getattr(g, "token_payload", {})
    jti = token_payload.get("jti")

    if jti:
        TokenService.revoke_session(jti)

    return ApiResponse.success(message=f"Successfully logged out user {user.email}.")


@donor_bp.route("/me", methods=["GET"])
@require_login
def get_current_user_profile():
    """
    Get current logged in user profile details.
    """
    user = get_current_user()
    return jsonify(user.to_dict()), 200


@donor_bp.route("/donor/dashboard-data", methods=["GET"])
@require_donor
def donor_dashboard_sample():
    """
    Protected Donor-only route test.
    """
    user = get_current_user()
    return jsonify({
        "message": f"Welcome to Donor Dashboard, {user.name}!",
        "donor_id": user.donor_profile.id if user.donor_profile else None,
        "blood_group": user.donor_profile.blood_group if user.donor_profile else None
    }), 200
