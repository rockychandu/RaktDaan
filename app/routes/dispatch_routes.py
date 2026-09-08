"""
Hospital Dispatch Logistics REST API Blueprints (Member 4).
Endpoints: /api/v1/dispatches
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_admin, get_current_user
from app.services.dispatch_service import DispatchService
from pydantic import ValidationError as PydanticValError

dispatch_api_bp = Blueprint("dispatch_api", __name__, url_prefix="/api/v1/dispatches")


@dispatch_api_bp.route("", methods=["GET"])
@require_admin
def list_dispatches():
    """List and paginate hospital dispatches."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    res = DispatchService.list_dispatches(page, per_page)
    return jsonify(res), 200


@dispatch_api_bp.route("", methods=["POST"])
@require_admin
def create_dispatch():
    """Create a new hospital dispatch order."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        dsp = DispatchService.create_dispatch(data, user_id=user.id)
        return jsonify(dsp.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@dispatch_api_bp.route("/<int:dispatch_id>", methods=["GET"])
@require_admin
def get_dispatch(dispatch_id: int):
    """Get dispatch order details."""
    dsp = DispatchService.get_dispatch_by_id(dispatch_id)
    return jsonify(dsp.to_dict()), 200
