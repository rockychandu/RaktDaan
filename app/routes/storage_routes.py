"""
Storage Location Hierarchy REST API Blueprints (Member 4).
Endpoints: /api/v1/storage
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin
from app.services.storage_service import StorageService
from pydantic import ValidationError as PydanticValError

storage_api_bp = Blueprint("storage_api", __name__, url_prefix="/api/v1/storage")


@storage_api_bp.route("/units", methods=["GET"])
@require_login
def list_storage_units():
    """List all storage units and capacities."""
    units = StorageService.list_storage_units()
    return jsonify({"units": units}), 200


@storage_api_bp.route("/units", methods=["POST"])
@require_admin
def create_storage_unit():
    """Create a new cold storage equipment unit."""
    data = request.get_json(silent=True) or {}
    try:
        unit = StorageService.create_storage_unit(data)
        return jsonify(unit.to_dict()), 201
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@storage_api_bp.route("/assign", methods=["POST"])
@require_admin
def assign_storage_location():
    """Assign a blood bag to a storage unit & shelf location."""
    data = request.get_json(silent=True) or {}
    try:
        bag, unit = StorageService.assign_bag_to_storage_location(data)
        return jsonify({"blood_bag": bag.to_dict(), "storage_unit": unit.to_dict()}), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422
