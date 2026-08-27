"""
Donation Workflow REST API Blueprints (Member 3).
Endpoints: /api/v1/donations
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.donation_service import DonationService
from app.services.donation_prescreening_service import DonorPrescreeningService
from app.schemas.donation_prescreening_schemas import HealthCheckupSchema
from pydantic import ValidationError as PydanticValError

donation_api_bp = Blueprint("donation_api", __name__, url_prefix="/api/v1/donations")


@donation_api_bp.route("", methods=["GET"])
@require_admin
def list_donations():
    """List and paginate donation records."""
    status = request.args.get("status")
    blood_group = request.args.get("blood_group")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = DonationService.list_all_donations(status, blood_group, page, per_page)
    return jsonify(result), 200


@donation_api_bp.route("/pending-admin", methods=["GET"])
def list_pending_admin_donations():
    """List passed pre-screened donor registrations for admin review."""
    result = DonorPrescreeningService.get_pending_admin_donations()
    return jsonify({
        "status": "success",
        "count": len(result),
        "data": result
    }), 200


@donation_api_bp.route("/prescreening", methods=["POST"])
@require_login
def submit_health_checkup_prescreening():
    """Donor self-checkup & pre-donation screening evaluation endpoint."""
    user = get_current_user()
    if not user.donor_profile:
        return jsonify({"detail": "User account does not have an active Donor Profile."}), 400

    data = request.get_json(silent=True) or {}
    try:
        schema = HealthCheckupSchema(**data)
        res = DonorPrescreeningService.evaluate_and_submit_prescreening(
            donor_profile_id=user.donor_profile.id,
            weight_kg=schema.weight_kg,
            hemoglobin_level=schema.hemoglobin_level,
            blood_pressure_sys=schema.blood_pressure_sys,
            blood_pressure_dia=schema.blood_pressure_dia,
            pulse_rate=schema.pulse_rate,
            temp_celsius=schema.temp_celsius,
            has_chronic_illness=schema.has_chronic_illness,
            is_on_medication=schema.is_on_medication,
            collection_center=schema.collection_center or "Central RaktDaan Blood Bank"
        )
        status_code = 200 if res["is_passed"] else 400
        return jsonify(res), status_code
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422
    except Exception as e:
        return jsonify({"detail": str(e)}), 400


@donation_api_bp.route("", methods=["POST"])
@require_login
def create_donation():
    """Register a new donation event."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        donation = DonationService.create_donation_registration(data, staff_user_id=user.id)
        return jsonify(donation.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@donation_api_bp.route("/<int:donation_id>/screening", methods=["PUT"])
@require_admin
def submit_screening(donation_id: int):
    """Submit medical screening vitals and update donation status."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        donation, screening = DonationService.submit_medical_screening(donation_id, data, staff_user_id=user.id)
        return jsonify({"donation": donation.to_dict(), "screening": screening.to_dict()}), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@donation_api_bp.route("/<int:donation_id>/start", methods=["POST"])
@require_admin
def start_donation(donation_id: int):
    """Start donation procedure (ELIGIBLE -> IN_PROGRESS)."""
    donation = DonationService.start_donation_procedure(donation_id)
    return jsonify(donation.to_dict()), 200


@donation_api_bp.route("/<int:donation_id>/complete", methods=["POST"])
@require_admin
def complete_donation(donation_id: int):
    """Complete donation procedure and auto-create BloodBag."""
    data = request.get_json(silent=True) or {}
    volume_ml = data.get("volume_ml", 450)
    donation, bag = DonationService.complete_donation_procedure(donation_id, volume_ml)
    return jsonify({"donation": donation.to_dict(), "blood_bag": bag.to_dict()}), 200


@donation_api_bp.route("/<int:donation_id>/cancel", methods=["POST"])
@require_login
def cancel_donation(donation_id: int):
    """Cancel a donation procedure."""
    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "Cancelled by user/staff")
    donation = DonationService.cancel_donation(donation_id, reason)
    return jsonify(donation.to_dict()), 200
