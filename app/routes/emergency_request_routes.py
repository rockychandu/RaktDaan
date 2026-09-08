"""
Emergency Request REST API Controller Blueprint.
Provides endpoints for creating emergency requests from Home Page / Portals,
retrieving admin & donor request lists, updating request status, and handling donor responses.
"""

from flask import Blueprint, request, jsonify, g
from app.services.emergency_request_service import EmergencyRequestService

emergency_request_api_bp = Blueprint("emergency_request_api", __name__)


from flask import session

# 1. CREATE EMERGENCY REQUEST (Home Page / Portals)
@emergency_request_api_bp.route("/api/emergency-requests", methods=["POST"])
@emergency_request_api_bp.route("/api/v1/emergency-requests", methods=["POST"])
def create_emergency_request():
    """
    Creates an emergency blood request.
    Stores request persistently in DB, generates unique ER-2026-XXXXXX ID, sets status to PENDING.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request payload."}), 400

    blood_group = data.get("blood_group")
    hospital_name = data.get("hospital_name")
    
    if not blood_group or not hospital_name:
        return jsonify({"status": "error", "message": "Blood group and hospital name are required."}), 400

    user_id = getattr(g, "current_user_id", None) or session.get("user_id")
    
    try:
        req = EmergencyRequestService.create_request(data, user_id=user_id)
        if req and req.request_code:
            session_codes = session.get("created_request_codes", [])
            if req.request_code not in session_codes:
                session_codes.append(req.request_code)
            session["created_request_codes"] = session_codes
            if data.get("requester_phone"):
                session["requester_phone"] = data.get("requester_phone")

        return jsonify({
            "status": "success",
            "message": f"Emergency request submitted successfully. Request ID: {req.request_code}",
            "request_id": req.request_code,
            "request_code": req.request_code,
            "data": req.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to create request: {str(e)}"}), 500


# 2. GET EMERGENCY REQUESTS FOR ADMIN
@emergency_request_api_bp.route("/api/admin/emergency-requests", methods=["GET"])
@emergency_request_api_bp.route("/api/v1/emergency-requests/admin", methods=["GET"])
def get_emergency_requests_admin():
    """
    Retrieves all emergency requests for Admin Portal with filter/search options.
    """
    blood_group = request.args.get("blood_group")
    status = request.args.get("status")
    urgency = request.args.get("urgency")
    search = request.args.get("search") or request.args.get("query")

    requests_list = EmergencyRequestService.get_all_requests_admin(
        blood_group=blood_group,
        status=status,
        urgency=urgency,
        search_query=search
    )
    
    return jsonify({
        "status": "success",
        "count": len(requests_list),
        "data": [r.to_dict() for r in requests_list]
    }), 200


# 3. GET EMERGENCY REQUESTS FOR DONORS
@emergency_request_api_bp.route("/api/donor/emergency-requests", methods=["GET"])
@emergency_request_api_bp.route("/api/v1/emergency-requests/donor", methods=["GET"])
def get_emergency_requests_donor():
    """
    Retrieves active emergency requests that donors are eligible to respond to.
    """
    blood_group = request.args.get("blood_group")
    requests_list = EmergencyRequestService.get_active_requests_donor(blood_group=blood_group)

    return jsonify({
        "status": "success",
        "count": len(requests_list),
        "data": [r.to_dict() for r in requests_list]
    }), 200


# 4. GET SPECIFIC EMERGENCY REQUEST DETAILS
@emergency_request_api_bp.route("/api/emergency-requests/<req_id>", methods=["GET"])
@emergency_request_api_bp.route("/api/v1/emergency-requests/<req_id>", methods=["GET"])
def get_emergency_request_details(req_id):
    """
    Retrieves complete details of a specific emergency request including donor responses.
    """
    req = EmergencyRequestService.get_by_code_or_id(req_id)
    if not req:
        return jsonify({"status": "error", "message": "Emergency Request not found."}), 404

    return jsonify({
        "status": "success",
        "data": req.to_dict()
    }), 200


# 5. UPDATE EMERGENCY REQUEST STATUS (Admin / Authorized)
@emergency_request_api_bp.route("/api/emergency-requests/<req_id>/status", methods=["PUT", "PATCH"])
@emergency_request_api_bp.route("/api/v1/emergency-requests/<req_id>/status", methods=["PUT", "PATCH"])
def update_emergency_request_status(req_id):
    """
    Updates the status of an emergency request (PENDING, APPROVED, ACTIVE, FULFILLED, REJECTED, CANCELLED, EXPIRED).
    """
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if not new_status:
        return jsonify({"status": "error", "message": "Status field is required."}), 400

    result = EmergencyRequestService.update_request_status(req_id, new_status)
    if not result.get("success"):
        return jsonify({"status": "error", "message": result.get("message")}), 400

    return jsonify({
        "status": "success",
        "message": result.get("message"),
        "data": result.get("request")
    }), 200


# 6. DONOR RESPONSE ("I CAN DONATE")
@emergency_request_api_bp.route("/api/emergency-requests/<req_id>/respond", methods=["POST"])
@emergency_request_api_bp.route("/api/v1/emergency-requests/<req_id>/respond", methods=["POST"])
def respond_to_emergency_request(req_id):
    """
    Records a donor's response ('I CAN DONATE') to an emergency request.
    """
    data = request.get_json(silent=True) or {}
    donor_name = data.get("donor_name", "Voluntary Donor")
    donor_phone = data.get("donor_phone", "9876543210")
    donor_blood_group = data.get("donor_blood_group", "O+")
    donor_id = data.get("donor_id")
    notes = data.get("notes")

    result = EmergencyRequestService.add_donor_response(
        request_id_or_code=req_id,
        donor_id=donor_id,
        donor_name=donor_name,
        donor_phone=donor_phone,
        donor_blood_group=donor_blood_group,
        notes=notes
    )

    if not result.get("success"):
        return jsonify({"status": "error", "message": result.get("message")}), 400

    return jsonify({
        "status": "success",
        "message": result.get("message"),
        "data": result.get("response")
    }), 200
