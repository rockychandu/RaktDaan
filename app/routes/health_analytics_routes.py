"""
Donor Health Trajectory & Cardiovascular Risk Analytics REST API Blueprint (Member 3).
"""

import logging
from flask import Blueprint, jsonify

from app.services.donor_health_analytics_engine import DonorHealthAnalyticsEngine

logger = logging.getLogger(__name__)

health_analytics_bp = Blueprint("health_analytics_bp", __name__, url_prefix="/api/donor-health")


@health_analytics_bp.route("/<int:donor_id>/trajectory", methods=["GET"])
def get_donor_health_trajectory(donor_id):
    res = DonorHealthAnalyticsEngine.analyze_donor_health_trajectory(donor_id)
    if "error" in res:
        return jsonify({"status": "error", "message": res["error"]}), 404
    return jsonify({"status": "success", "data": res}), 200
