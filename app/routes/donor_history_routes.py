"""
Donor History Timeline & Admin Monitoring REST API Blueprint.
Endpoints: /api/v1/donor-history
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.donor_history_event_service import DonorHistoryEventService
from app.services.donation_workflow_state_machine import DonationStateMachine

donor_history_api_bp = Blueprint("donor_history_api", __name__, url_prefix="/api/v1/donor-history")


@donor_history_api_bp.route("/me", methods=["GET"])
@require_login
def get_my_donor_history():
    """Returns chronological timeline history for the logged-in donor."""
    user = get_current_user()
    if not user.donor_profile:
        return jsonify({"status": "error", "message": "Donor profile not found"}), 404

    timeline = DonorHistoryEventService.get_donor_chronological_history(user.donor_profile.id)
    return jsonify({
        "status": "success",
        "count": len(timeline),
        "data": timeline
    }), 200


@donor_history_api_bp.route("/admin/donors", methods=["GET"])
@require_admin
def admin_search_donors():
    """Admin search and filter across donors, vitals, eligibility, and histories."""
    query_str = request.args.get("query")
    blood_group = request.args.get("blood_group")
    eligibility_status = request.args.get("eligibility_status")
    donation_status = request.args.get("donation_status")

    results = DonorHistoryEventService.admin_search_and_filter_donors(
        query_str=query_str,
        blood_group=blood_group,
        eligibility_status=eligibility_status,
        donation_status=donation_status
    )
    return jsonify({
        "status": "success",
        "count": len(results),
        "data": results
    }), 200


@donor_history_api_bp.route("/admin/transition", methods=["POST"])
@require_admin
def admin_transition_donation_state():
    """Admin executes donation workflow state transition (e.g. APPROVED -> COLLECTED -> COMPLETED)."""
    payload = request.get_json(silent=True) or {}
    donation_id = payload.get("donation_id")
    target_status = payload.get("target_status")
    remarks = payload.get("remarks", "Updated by Admin")
    volume_ml = payload.get("volume_ml", 450)

    if not donation_id or not target_status:
        return jsonify({"status": "error", "message": "donation_id and target_status are required"}), 400

    user = get_current_user()
    try:
        res = DonationStateMachine.transition(
            donation_id=donation_id,
            target_status=target_status,
            staff_user_id=user.id,
            remarks=remarks,
            volume_ml=volume_ml
        )
        return jsonify({
            "status": "success",
            "message": f"Successfully updated donation status to '{target_status}'.",
            "data": res
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
