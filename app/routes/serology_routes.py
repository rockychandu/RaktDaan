"""
REST API Blueprint for Laboratory Serology Testing (Member 3 & Member 4).
"""

from flask import Blueprint, request, jsonify
from app.database.models.serology import SerologyTestRecord
from app.services.serology_testing_engine import SerologyTestingEngine
from app.common.exceptions import DomainException

serology_api_bp = Blueprint("serology_api", __name__, url_prefix="/api/serology")


@serology_api_bp.route("/records", methods=["GET"])
@serology_api_bp.route("/v1/records", methods=["GET"])
def get_serology_records():
    """
    Retrieves all serology test records for Admin Portal.
    """
    records = SerologyTestRecord.query.order_by(SerologyTestRecord.id.desc()).all()
    return jsonify({
        "status": "success",
        "count": len(records),
        "data": [r.to_dict() for r in records]
    }), 200


@serology_api_bp.route("/submit", methods=["POST"])
def submit_serology_test():
    """
    Submits serology lab test results for a blood bag.
    """
    try:
        data = request.get_json() or {}
        bag_id = data.get("bag_id")
        if not bag_id:
            return jsonify({"status": "error", "message": "Field 'bag_id' is required."}), 400

        record = SerologyTestingEngine.submit_lab_test_results(
            bag_id=int(bag_id),
            hiv_result=data.get("hiv_result", "NON_REACTIVE"),
            hbsag_result=data.get("hbsag_result", "NON_REACTIVE"),
            hcv_result=data.get("hcv_result", "NON_REACTIVE"),
            vdrl_result=data.get("vdrl_result", "NON_REACTIVE"),
            malaria_result=data.get("malaria_result", "NON_REACTIVE"),
            nat_test_result=data.get("nat_test_result", "NEGATIVE"),
            technician_user_id=data.get("technician_user_id", 1),
            lab_notes=data.get("lab_notes")
        )
        return jsonify({"status": "success", "data": record.to_dict()}), 201
    except DomainException as e:
        return jsonify({"status": "error", "message": e.message}), e.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
