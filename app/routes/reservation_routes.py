"""
Blood Reservation REST API Blueprints (Member 4).
Endpoints: /api/v1/reservations
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.reservation_service import ReservationService
from app.database.models.inventory_extended import BloodReservation
from pydantic import ValidationError as PydanticValError

reservation_api_bp = Blueprint("reservation_api", __name__, url_prefix="/api/v1/reservations")


@reservation_api_bp.route("", methods=["GET"])
@require_admin
def list_reservations():
    """List blood reservations."""
    rsvs = BloodReservation.query.filter_by(is_deleted=False).order_by(BloodReservation.created_at.desc()).all()
    return jsonify([r.to_dict() for r in rsvs]), 200


@reservation_api_bp.route("", methods=["POST"])
@require_admin
def create_reservation():
    """Create FEFO blood reservation."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        rsv = ReservationService.create_reservation(data, user_id=user.id)
        return jsonify(rsv.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@reservation_api_bp.route("/<int:reservation_id>/release", methods=["PATCH"])
@require_admin
def release_reservation(reservation_id: int):
    """Release a blood reservation."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    reason = data.get("reason", "Manual Release")
    rsv = ReservationService.release_reservation(reservation_id, reason=reason, user_id=user.id)
    return jsonify(rsv.to_dict()), 200
