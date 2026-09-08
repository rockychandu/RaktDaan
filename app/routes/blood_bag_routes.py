"""
Blood Bag Lifecycle REST API Blueprints (Member 4).
Endpoints: /api/v1/blood-bags
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.blood_bag_service import BloodBagService
from pydantic import ValidationError as PydanticValError

blood_bag_api_bp = Blueprint("blood_bag_api", __name__, url_prefix="/api/v1/blood-bags")


@blood_bag_api_bp.route("", methods=["GET"])
@require_login
def list_blood_bags():
    """List, search, filter, and paginate blood bags."""
    args = request.args.to_dict()
    res = BloodBagService.search_blood_bags(args)
    return jsonify(res), 200


@blood_bag_api_bp.route("/<int:bag_id>", methods=["GET"])
@require_login
def get_blood_bag(bag_id: int):
    """Get blood bag details."""
    bag = BloodBagService.get_bag_by_id(bag_id)
    return jsonify(bag.to_dict()), 200


@blood_bag_api_bp.route("/<int:bag_id>/status", methods=["PATCH"])
@require_admin
def update_bag_status(bag_id: int):
    """Transition blood bag status state machine."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        bag = BloodBagService.transition_bag_status(
            bag_id=bag_id,
            target_status=data.get("status"),
            reason=data.get("reason", "Manual Admin Status Transition"),
            changed_by_user_id=user.id,
            notes=data.get("notes")
        )
        return jsonify(bag.to_dict()), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@blood_bag_api_bp.route("/<int:bag_id>/tracking", methods=["GET"])
@require_login
def get_bag_tracking_timeline(bag_id: int):
    """Get chronological visual traceability timeline for a blood bag."""
    timeline = BloodBagService.get_bag_traceability_timeline(bag_id)
    return jsonify(timeline), 200
