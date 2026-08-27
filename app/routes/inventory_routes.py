"""
Blood Inventory REST API Blueprints (Member 4).
Endpoints: /api/v1/inventory
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.inventory_service import InventoryService
from app.services.expiry_engine import ExpiryEngine
from app.services.low_stock_engine import LowStockEngine
from app.services.inventory_transaction_service import InventoryTransactionService
from app.services.reconciliation_service import ReconciliationService
from pydantic import ValidationError as PydanticValError

inventory_api_bp = Blueprint("inventory_api", __name__, url_prefix="/api/v1/inventory")


@inventory_api_bp.route("", methods=["GET"])
@inventory_api_bp.route("/summary", methods=["GET"])
@require_login
def get_inventory_summary():
    """Retrieve full aggregate blood inventory summary."""
    summary = InventoryService.get_inventory_summary()
    return jsonify(summary), 200


@inventory_api_bp.route("/blood-group/<string:blood_group>", methods=["GET"])
@require_login
def get_blood_group_inventory(blood_group: str):
    """Retrieve aggregate inventory for a specific blood group."""
    inv = InventoryService.recalculate_aggregate_inventory_for_blood_group(blood_group)
    return jsonify(inv.to_dict()), 200


@inventory_api_bp.route("/low-stock", methods=["GET"])
@require_admin
def evaluate_low_stock():
    """Evaluate low stock thresholds across all blood groups."""
    evaluations = LowStockEngine.evaluate_stock_levels()
    return jsonify({"evaluations": evaluations}), 200


@inventory_api_bp.route("/thresholds", methods=["PUT"])
@require_admin
def update_stock_threshold():
    """Update minimum and critical stock thresholds."""
    data = request.get_json(silent=True) or {}
    try:
        thresh = LowStockEngine.update_threshold_config(data)
        return jsonify(thresh.to_dict()), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422


@inventory_api_bp.route("/expiring", methods=["GET"])
@require_admin
def get_expiring_soon():
    """Run automatic expiry scanner and get expiring bags."""
    days = int(request.args.get("days", 7))
    res = ExpiryEngine.run_automatic_expiry_check(warning_days=days)
    return jsonify(res), 200


@inventory_api_bp.route("/transactions", methods=["GET"])
@require_admin
def list_transactions():
    """Query inventory transaction audit ledger."""
    args = request.args.to_dict()
    res = InventoryTransactionService.list_transactions(args)
    return jsonify(res), 200


@inventory_api_bp.route("/reconcile", methods=["POST"])
@require_admin
def reconcile_physical_stock():
    """Execute physical inventory reconciliation audit."""
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    try:
        results = ReconciliationService.execute_stock_reconciliation(data, user_id=user.id)
        return jsonify({"results": results}), 200
    except PydanticValError as ve:
        return jsonify({"detail": ve.errors()}), 422
