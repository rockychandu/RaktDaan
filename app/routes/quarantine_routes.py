"""
Quarantine & Safety Isolation REST API Blueprints (Member 4).
Endpoints: /api/v1/quarantine
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_admin, get_current_user
from app.services.quarantine_service import QuarantineService
from pydantic import ValidationError as PydanticValError

quarantine_api_bp = Blueprint("quarantine_api", __name__, url_prefix="/api/v1/quarantine")


@quarantine_api_bp.route("", methods=["GET"])
@require_admin
def list_quarantines():
    """List active quarantine isolation records."""
    records = QuarantineService.list_active_quarantines()
    return jsonify({"active_quarantines": records}), 200


@quarantine_api_bp.route("", methods=["POST"])
@require_admin
def create_quarantine():
    """Place a blood bag into quarantine isolation."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        record = QuarantineService.place_bag_in_quarantine(data, user_id=user.id)
        return jsonify(record.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@quarantine_api_bp.route("/<int:quarantine_id>/resolve", methods=["PATCH"])
@require_admin
def resolve_quarantine(quarantine_id: int):
    """Resolve a quarantine record (Release or Discard)."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        record = QuarantineService.resolve_quarantine(quarantine_id, data, user_id=user.id)
        return jsonify(record.to_dict()), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422
