"""
REST API Blueprint for Transfusion Safety, Cross-Matching, and Deferral Management (Member 3 & Member 4).
"""

from flask import Blueprint, request, jsonify
from app.services.cross_match_engine import CrossMatchEngine
from app.services.adverse_event_engine import AdverseEventEngine
from app.services.donor_deferral_engine import DonorDeferralEngine
from app.services.transfusion_safety_engine import TransfusionSafetyEngine
from app.services.inventory_reconciliation_deep_engine import InventoryReconciliationDeepEngine
from app.common.exceptions import DomainException

safety_deferral_api_bp = Blueprint("safety_deferral_api", __name__, url_prefix="/api/safety")


@safety_deferral_api_bp.route("/cross-match", methods=["POST"])
def perform_cross_match():
    """
    Performs serological cross-match and antibody screen.
    """
    try:
        data = request.get_json() or {}
        bag_id = data.get("bag_id")
        recipient_blood_group = data.get("recipient_blood_group")
        recipient_name = data.get("recipient_name", "Patient")
        if not bag_id or not recipient_blood_group:
            return jsonify({"status": "error", "message": "Fields 'bag_id' and 'recipient_blood_group' are required."}), 400

        res = CrossMatchEngine.perform_cross_match(
            bag_id=int(bag_id),
            recipient_blood_group=recipient_blood_group,
            recipient_name=recipient_name,
            coombs_test_result=data.get("coombs_test_result", "NEGATIVE"),
            antibody_screen_result=data.get("antibody_screen_result", "NEGATIVE"),
            technician_user_id=data.get("technician_user_id", 1)
        )
        return jsonify({"status": "success", "data": res}), 200
    except DomainException as e:
        return jsonify({"status": "error", "message": e.message}), e.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@safety_deferral_api_bp.route("/bedside-verify", methods=["POST"])
def bedside_verify():
    """
    Executes bedside transfusion 2-person safety check.
    """
    try:
        data = request.get_json() or {}
        bag_code = data.get("bag_code")
        patient_name = data.get("patient_name")
        patient_blood_group = data.get("patient_blood_group")
        if not bag_code or not patient_name or not patient_blood_group:
            return jsonify({"status": "error", "message": "Fields 'bag_code', 'patient_name', and 'patient_blood_group' are required."}), 400

        res = TransfusionSafetyEngine.verify_bedside_safety(
            bag_code=bag_code,
            patient_name=patient_name,
            patient_blood_group=patient_blood_group,
            verifier_1_user_id=data.get("verifier_1_user_id", 1),
            verifier_2_user_id=data.get("verifier_2_user_id", 2)
        )
        return jsonify({"status": "success", "data": res}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@safety_deferral_api_bp.route("/deferral/apply-temporary", methods=["POST"])
def apply_temporary_deferral():
    """
    Applies temporary deferral to donor.
    """
    try:
        data = request.get_json() or {}
        donor_id = data.get("donor_id")
        reason = data.get("reason")
        deferral_days = data.get("deferral_days", 30)
        if not donor_id or not reason:
            return jsonify({"status": "error", "message": "Fields 'donor_id' and 'reason' are required."}), 400

        record = DonorDeferralEngine.apply_temporary_deferral(
            donor_id=int(donor_id),
            reason=reason,
            deferral_days=int(deferral_days),
            notes=data.get("notes")
        )
        return jsonify({"status": "success", "data": record.to_dict()}), 201
    except DomainException as e:
        return jsonify({"status": "error", "message": e.message}), e.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@safety_deferral_api_bp.route("/deferral/evaluate-reinstatement/<int:donor_id>", methods=["GET"])
def evaluate_reinstatement(donor_id: int):
    """
    Evaluates reinstatement status for a deferred donor.
    """
    try:
        res = DonorDeferralEngine.evaluate_reinstatement(donor_id)
        return jsonify({"status": "success", "data": res}), 200
    except DomainException as e:
        return jsonify({"status": "error", "message": e.message}), e.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@safety_deferral_api_bp.route("/reconcile-discrepancies", methods=["GET", "POST"])
def reconcile_discrepancies():
    """
    Analyzes physical stock discrepancies and synchronizes aggregate inventory counts.
    """
    try:
        if request.method == "POST":
            updated_count = InventoryReconciliationDeepEngine.synchronize_inventory_counts()
            return jsonify({"status": "success", "message": f"Successfully synchronized {updated_count} blood group inventory counts."}), 200

        res = InventoryReconciliationDeepEngine.analyze_stock_discrepancies()
        return jsonify({"status": "success", "data": res}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
