"""
REST API Blueprint for Cold Chain Surveillance & Temperature Sensors (Member 4).
"""

from flask import Blueprint, request, jsonify
from app.database.models.cold_chain import TemperatureSensorLog
from app.services.cold_chain_monitoring_engine import ColdChainMonitoringEngine
from app.common.exceptions import DomainException

cold_chain_api_bp = Blueprint("cold_chain_api", __name__, url_prefix="/api/cold-chain")


@cold_chain_api_bp.route("/logs", methods=["GET"])
@cold_chain_api_bp.route("/v1/logs", methods=["GET"])
def get_cold_chain_logs():
    """
    Retrieves cold chain IoT temperature sensor logs for Admin Portal.
    """
    logs = TemperatureSensorLog.query.order_by(TemperatureSensorLog.id.desc()).limit(100).all()
    return jsonify({
        "status": "success",
        "count": len(logs),
        "data": [l.to_dict() for l in logs]
    }), 200


@cold_chain_api_bp.route("/record-temp", methods=["POST"])
def record_temperature():
    """
    Records a sensor temperature reading for a cold storage unit.
    """
    try:
        data = request.get_json() or {}
        storage_unit_id = data.get("storage_unit_id")
        temp_celsius = data.get("reading_temp_celsius")
        if storage_unit_id is None or temp_celsius is None:
            return jsonify({"status": "error", "message": "Fields 'storage_unit_id' and 'reading_temp_celsius' are required."}), 400

        log = ColdChainMonitoringEngine.record_temperature_reading(
            storage_unit_id=int(storage_unit_id),
            temp_celsius=float(temp_celsius),
            notes=data.get("notes")
        )
        return jsonify({"status": "success", "data": log.to_dict()}), 201
    except DomainException as e:
        return jsonify({"status": "error", "message": e.message}), e.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
