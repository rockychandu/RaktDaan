"""
Hospital Return & Safety Recall REST API Blueprints (Member 4).
Endpoints: /api/v1/returns
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_admin, get_current_user
from app.services.return_recall_service import ReturnRecallService
from pydantic import ValidationError as PydanticValError

return_api_bp = Blueprint("return_api", __name__, url_prefix="/api/v1/returns")


@return_api_bp.route("", methods=["GET"])
@require_admin
def list_returns():
    """List hospital return and safety recall records."""
    records = ReturnRecallService.list_returns()
    return jsonify({"returns": records}), 200


@return_api_bp.route("", methods=["POST"])
@require_admin
def create_return():
    """Process a hospital blood return or recall inspection."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        record = ReturnRecallService.process_return_or_recall(data, user_id=user.id)
        return jsonify(record.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422
