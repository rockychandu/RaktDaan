"""
REST API Blueprint for Hospital SLA, Demand Forecasting, and Regulatory Audits (Member 4).
"""

from flask import Blueprint, request, jsonify
from app.services.hospital_sla_engine import HospitalSLAEngine
from app.services.demand_forecasting_engine import DemandForecastingEngine
from app.services.compliance_audit_engine import ComplianceAuditEngine

sla_forecasting_api_bp = Blueprint("sla_forecasting_api", __name__, url_prefix="/api/operations")


@sla_forecasting_api_bp.route("/demand-forecast", methods=["GET"])
def get_demand_forecast():
    """
    Returns 30-day moving average blood demand forecast and safety stock metrics.
    """
    days_window = request.args.get("days_window", default=30, type=int)
    res = DemandForecastingEngine.calculate_blood_demand_forecast(days_window=days_window)
    return jsonify({"status": "success", "data": res}), 200


@sla_forecasting_api_bp.route("/sla-performance", methods=["GET"])
def get_sla_performance():
    """
    Returns hospital request fulfillment SLA metrics and turnaround times.
    """
    res = HospitalSLAEngine.calculate_hospital_sla_performance()
    return jsonify({"status": "success", "data": res}), 200


@sla_forecasting_api_bp.route("/compliance-audit", methods=["GET"])
def get_compliance_audit():
    """
    Executes WHO/FDA blood bank regulatory compliance audit.
    """
    res = ComplianceAuditEngine.run_compliance_audit()
    return jsonify({"status": "success", "data": res}), 200
