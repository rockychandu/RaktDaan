"""
Inventory Analytics & Performance REST API Blueprints (Member 4).
Endpoints: /api/v1/analytics
"""

from flask import Blueprint, jsonify
from app.auth.dependencies import require_admin
from app.services.inventory_analytics_engine import InventoryAnalyticsEngine

analytics_api_bp = Blueprint("analytics_api", __name__, url_prefix="/api/v1/analytics")


@analytics_api_bp.route("/dashboard", methods=["GET"])
@require_admin
def get_analytics_overview():
    """Retrieves operational analytics overview (wastage, utilization, storage duration)."""
    analytics = InventoryAnalyticsEngine.get_inventory_analytics_overview()
    return jsonify(analytics), 200
