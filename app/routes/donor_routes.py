"""
Donor Management REST API Blueprints (Member 3).
Endpoints: /api/v1/donors
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.donor_service import DonorService
from app.services.eligibility_engine import DonorEligibilityEngine
from app.services.donor_analytics_service import DonorAnalyticsService
from app.auth.validators import ValidationError
from pydantic import ValidationError as PydanticValError

donor_api_bp = Blueprint("donor_api", __name__, url_prefix="/api/v1/donors")


@donor_api_bp.route("", methods=["GET"])
@require_admin
def list_donors():
    """List, filter, search, and paginate donors."""
    args = request.args.to_dict()
    result = DonorService.search_donors(args)
    return jsonify(result), 200


@donor_api_bp.route("", methods=["POST"])
@require_admin
def create_donor():
    """Admin endpoint to create/register a donor."""
    data = request.get_json(silent=True) or {}
    try:
        user, donor = DonorService.register_donor(data)
        return jsonify(donor.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@donor_api_bp.route("/<int:donor_id>", methods=["GET"])
@require_login
def get_donor(donor_id: int):
    """Get donor profile details."""
    donor = DonorService.get_donor_by_id(donor_id)
    return jsonify(donor.to_dict()), 200


@donor_api_bp.route("/<int:donor_id>", methods=["PUT"])
@require_login
def update_donor(donor_id: int):
    """Update donor profile."""
    data = request.get_json(silent=True) or {}
    try:
        donor = DonorService.update_donor_profile(donor_id, data)
        return jsonify(donor.to_dict()), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@donor_api_bp.route("/<int:donor_id>", methods=["DELETE"])
@require_admin
def soft_delete_donor(donor_id: int):
    """Soft delete/deactivate a donor."""
    DonorService.soft_delete_donor(donor_id)
    return jsonify({"success": True, "message": f"Donor {donor_id} deactivated successfully."}), 200


@donor_api_bp.route("/<int:donor_id>/restore", methods=["POST"])
@require_admin
def restore_donor(donor_id: int):
    """Restore a soft-deleted donor."""
    donor = DonorService.restore_donor(donor_id)
    return jsonify(donor.to_dict()), 200


@donor_api_bp.route("/<int:donor_id>/eligibility", methods=["POST"])
@require_admin
def evaluate_eligibility(donor_id: int):
    """Evaluates donor eligibility against criteria and logs history."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    result = DonorEligibilityEngine.evaluate_eligibility(
        donor_id=donor_id,
        weight_kg=data.get("weight_kg"),
        hemoglobin_level=data.get("hemoglobin_level"),
        bp_sys=data.get("blood_pressure_sys"),
        bp_dia=data.get("blood_pressure_dia"),
        pulse_rate=data.get("pulse_rate"),
        has_chronic_illness=data.get("has_chronic_illness", False),
        is_on_medication=data.get("is_on_medication", False),
        evaluator_staff_id=user.id
    )
    return jsonify(result), 200


@donor_api_bp.route("/statistics", methods=["GET"])
@require_admin
def get_donor_statistics():
    """Retrieves donor module KPI statistics."""
    stats = DonorAnalyticsService.get_donor_dashboard_statistics()
    return jsonify(stats), 200
