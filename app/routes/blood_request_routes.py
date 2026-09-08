"""
Blood Request REST API Controller Blueprint.
Member 4 — Requester / Blood Request Module.

Provides comprehensive REST API endpoints for:
- Blood request creation, editing, cancellation, tracking, and details
- Requester dashboard analytics and request history
- Admin review, approval, status state transitions, and fulfillment management
- Eligible donor matching and donor mobile response tracking
- User notification center management (unread count, mark read, mark all read)
- Clinical document uploads with security validation
"""

from flask import Blueprint, request, jsonify, g
from app.services.blood_request_service import BloodRequestService
from app.database.models.blood_request import BloodRequest, BloodRequestDonorMatch, RequestNotification
from app.database.connection import db

blood_request_api_bp = Blueprint("blood_request_api", __name__)


from flask import session

# -------------------------------------------------------------------------
# 1. CREATE BLOOD REQUEST (Home Page / Requester Portal)
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/blood-requests", methods=["POST"])
@blood_request_api_bp.route("/api/v1/blood-requests", methods=["POST"])
def create_blood_request():
    """
    Creates a new comprehensive Blood Request with 5-section validation and duplicate detection.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"status": "error", "message": "Invalid or empty JSON request payload."}), 400

    user_id = getattr(g, "current_user_id", None) or session.get("user_id")
    result = BloodRequestService.create_blood_request(data, user_id=user_id)

    if result.get("success") and result.get("public_request_id"):
        req_code = result["public_request_id"]
        session_codes = session.get("created_request_codes", [])
        if req_code not in session_codes:
            session_codes.append(req_code)
        session["created_request_codes"] = session_codes
        if data.get("requester_phone"):
            session["requester_phone"] = data.get("requester_phone")

    status_code = result.get("status_code", 201 if result.get("success") else 400)
    return jsonify({
        "status": "success" if result.get("success") else "error",
        "message": result.get("message"),
        "request_id": result.get("public_request_id"),
        "is_duplicate": result.get("is_duplicate", False),
        "data": result.get("data")
    }), status_code


# -------------------------------------------------------------------------
# 2. GET REQUESTER DASHBOARD & METRICS (PRIVACY ENFORCED)
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/requester/dashboard", methods=["GET"])
@blood_request_api_bp.route("/api/v1/requester/dashboard", methods=["GET"])
def get_requester_dashboard():
    """
    Returns dashboard summary metrics and recent requests strictly for the current requester.
    If no user session or request exists, returns empty metrics for requester privacy.
    """
    user_id = getattr(g, "current_user_id", None) or session.get("user_id")
    session_phone = session.get("requester_phone")
    created_codes = session.get("created_request_codes", [])

    query = BloodRequest.query

    if user_id:
        query = query.filter(BloodRequest.requester_id == user_id)
    elif session_phone or created_codes:
        filters = []
        if session_phone:
            filters.append(BloodRequest.requester_phone == session_phone)
        if created_codes:
            filters.append(BloodRequest.public_request_id.in_(created_codes))
        query = query.filter(db.or_(*filters))
    else:
        # Privacy guard: Anonymous viewer without requests sees 0 metrics
        return jsonify({
            "status": "success",
            "metrics": {
                "total_requests": 0,
                "active_requests": 0,
                "pending_requests": 0,
                "approved_requests": 0,
                "fulfilled_requests": 0,
                "emergency_requests": 0
            },
            "recent_requests": []
        }), 200

    total_requests = query.count()
    pending_requests = query.filter_by(status="SUBMITTED").count()
    active_requests = query.filter(BloodRequest.status.in_(["SUBMITTED", "UNDER_REVIEW", "VERIFIED", "APPROVED", "MATCHING_DONORS", "DONOR_NOTIFIED", "PARTIALLY_FULFILLED"])).count()
    approved_requests = query.filter_by(status="APPROVED").count()
    fulfilled_requests = query.filter_by(status="FULFILLED").count()
    emergency_requests = query.filter(BloodRequest.urgency.in_(["EMERGENCY", "CRITICAL"])).count()

    recent_requests = query.order_by(BloodRequest.created_at.desc()).limit(15).all()

    return jsonify({
        "status": "success",
        "metrics": {
            "total_requests": total_requests,
            "active_requests": active_requests,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests,
            "fulfilled_requests": fulfilled_requests,
            "emergency_requests": emergency_requests
        },
        "recent_requests": [r.to_dict() for r in recent_requests]
    }), 200


# -------------------------------------------------------------------------
# 2.5 GET ACTIVE BLOOD REQUESTS FOR DONOR PORTAL
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/donor/blood-requests", methods=["GET"])
@blood_request_api_bp.route("/api/v1/donor/blood-requests", methods=["GET"])
def get_donor_blood_requests():
    """
    Retrieves active blood requests so voluntary donors can view and respond ('I Can Donate').
    """
    blood_group = request.args.get("blood_group")
    query = BloodRequest.query.filter(BloodRequest.status.in_(["SUBMITTED", "UNDER_REVIEW", "VERIFIED", "APPROVED", "MATCHING_DONORS", "DONOR_NOTIFIED", "PARTIALLY_FULFILLED"]))
    if blood_group and blood_group.strip():
        query = query.filter_by(blood_group=blood_group.strip().upper())

    requests_list = query.order_by(BloodRequest.created_at.desc()).all()
    return jsonify({
        "status": "success",
        "count": len(requests_list),
        "data": [r.to_dict(include_relationships=True) for r in requests_list]
    }), 200


# -------------------------------------------------------------------------
# 3. GET BLOOD REQUESTS (History, Search, Filtering & Pagination)
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/blood-requests", methods=["GET"])
@blood_request_api_bp.route("/api/v1/blood-requests", methods=["GET"])
def get_blood_requests():
    """
    Retrieves paginated list of blood requests with filters: blood_group, status, urgency, hospital, date_range.
    """
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    blood_group = request.args.get("blood_group")
    status = request.args.get("status")
    urgency = request.args.get("urgency")
    hospital = request.args.get("hospital")
    search = request.args.get("search") or request.args.get("query")
    sort_by = request.args.get("sort_by", "newest")

    query = BloodRequest.query

    if blood_group and blood_group.strip():
        query = query.filter(BloodRequest.blood_group == blood_group.strip().upper())

    if status and status.strip():
        query = query.filter(BloodRequest.status == status.strip().upper())

    if urgency and urgency.strip():
        query = query.filter(BloodRequest.urgency == urgency.strip().upper())

    if hospital and hospital.strip():
        query = query.filter(BloodRequest.hospital_name.ilike(f"%{hospital.strip()}%"))

    if search and search.strip():
        q = f"%{search.strip()}%"
        query = query.filter(
            (BloodRequest.public_request_id.ilike(q)) |
            (BloodRequest.patient_name.ilike(q)) |
            (BloodRequest.requester_name.ilike(q)) |
            (BloodRequest.hospital_name.ilike(q))
        )

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(BloodRequest.created_at.asc())
    elif sort_by == "highest_priority":
        query = query.order_by(BloodRequest.urgency.desc(), BloodRequest.created_at.desc())
    else:
        query = query.order_by(BloodRequest.created_at.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "status": "success",
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "per_page": paginated.per_page,
        "data": [r.to_dict() for r in paginated.items]
    }), 200


# -------------------------------------------------------------------------
# 4. GET SPECIFIC BLOOD REQUEST DETAILS & TRACKING TIMELINE
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/blood-requests/<req_id>", methods=["GET"])
@blood_request_api_bp.route("/api/v1/blood-requests/<req_id>", methods=["GET"])
def get_blood_request_details(req_id):
    """
    Retrieves complete request details including donor matches, status history timeline, and documents.
    """
    req = BloodRequestService.get_request_by_id_or_code(req_id)
    if not req:
        return jsonify({"status": "error", "message": "Blood Request not found."}), 404

    return jsonify({
        "status": "success",
        "data": req.to_dict(include_relationships=True)
    }), 200


# -------------------------------------------------------------------------
# 5. EDIT BLOOD REQUEST (Requester / Authorized)
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/blood-requests/<req_id>", methods=["PUT", "PATCH"])
@blood_request_api_bp.route("/api/v1/blood-requests/<req_id>", methods=["PUT", "PATCH"])
def edit_blood_request(req_id):
    """
    Edits an active blood request before final fulfillment.
    """
    req = BloodRequestService.get_request_by_id_or_code(req_id)
    if not req:
        return jsonify({"status": "error", "message": "Blood Request not found."}), 404

    if req.status in ["FULFILLED", "CANCELLED", "REJECTED"]:
        return jsonify({"status": "error", "message": f"Cannot edit request in '{req.status}' state."}), 400

    data = request.get_json(silent=True) or {}
    for key in ["patient_name", "patient_age", "patient_gender", "hospital_name", "hospital_city", "required_date", "units_required", "medical_condition", "doctor_name"]:
        if key in data:
            setattr(req, key, data[key])

    req.units_remaining = max(0, req.units_required - req.units_collected)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Blood Request {req.public_request_id} updated successfully.",
        "data": req.to_dict()
    }), 200


# -------------------------------------------------------------------------
# 6. CANCEL BLOOD REQUEST
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/blood-requests/<req_id>/cancel", methods=["POST", "DELETE"])
@blood_request_api_bp.route("/api/v1/blood-requests/<req_id>/cancel", methods=["POST", "DELETE"])
def cancel_blood_request(req_id):
    """
    Cancels a blood request with reason.
    """
    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "Cancelled by user")
    user_id = getattr(g, "current_user_id", None)

    result = BloodRequestService.update_request_status(
        request_id_or_code=req_id,
        new_status="CANCELLED",
        changed_by_user_id=user_id,
        note=reason
    )

    if not result.get("success"):
        return jsonify({"status": "error", "message": result.get("message")}), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "message": result.get("message"),
        "data": result.get("data")
    }), 200


# -------------------------------------------------------------------------
# 7. ADMIN BLOOD REQUEST MANAGEMENT & APPROVAL / REJECTION / FULFILLMENT
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/admin/blood-requests", methods=["GET"])
@blood_request_api_bp.route("/api/v1/admin/blood-requests", methods=["GET"])
def get_admin_blood_requests():
    """
    Retrieves all blood requests for Admin Portal with status & priority breakdown.
    Auto-syncs any legacy/un-synced EmergencyRequests so every single request appears.
    """
    try:
        from app.database.models.emergency_request import EmergencyRequest
        emg_list = EmergencyRequest.query.all()
        for emg in emg_list:
            existing = BloodRequest.query.filter(
                (BloodRequest.public_request_id == emg.request_code) |
                (BloodRequest.patient_name == emg.patient_name)
            ).first()
            if not existing:
                br = BloodRequest(
                    public_request_id=emg.request_code,
                    requester_id=emg.requester_id,
                    requester_name=emg.requester_name,
                    requester_phone=emg.requester_phone,
                    requester_email=emg.requester_email or "",
                    relationship_with_patient="Emergency Contact",
                    patient_name=emg.patient_name,
                    patient_age=emg.patient_age or 30,
                    patient_gender="Male",
                    blood_group=emg.blood_group,
                    component="Whole Blood",
                    units_required=emg.units_required,
                    units_collected=0,
                    units_remaining=emg.units_required,
                    hospital_name=emg.hospital_name,
                    hospital_address=emg.hospital_address or "",
                    hospital_city=emg.hospital_city or "Central",
                    required_date=emg.created_at.strftime("%Y-%m-%d") if emg.created_at else "Immediate",
                    required_time=emg.required_datetime or "Immediate",
                    urgency=emg.urgency_level or "HIGH",
                    emergency_reason=emg.additional_reason or "Emergency Request",
                    status=emg.status if emg.status in ["SUBMITTED", "APPROVED", "FULFILLED", "REJECTED", "CANCELLED"] else "SUBMITTED"
                )
                db.session.add(br)
        db.session.commit()
    except Exception as sync_err:
        db.session.rollback()

    requests_list = BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()
    return jsonify({
        "status": "success",
        "count": len(requests_list),
        "data": [r.to_dict(include_relationships=True) for r in requests_list]
    }), 200


@blood_request_api_bp.route("/api/admin/blood-requests/<req_id>/status", methods=["PATCH", "PUT"])
@blood_request_api_bp.route("/api/v1/admin/blood-requests/<req_id>/status", methods=["PATCH", "PUT"])
def update_admin_blood_request_status(req_id):
    """
    Admin updates blood request status and units collected.
    """
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    note = data.get("note")
    units_collected = data.get("units_collected")
    admin_user_id = getattr(g, "current_user_id", None)

    if not new_status:
        return jsonify({"status": "error", "message": "Status field is required."}), 400

    result = BloodRequestService.update_request_status(
        request_id_or_code=req_id,
        new_status=new_status,
        changed_by_user_id=admin_user_id,
        note=note,
        units_collected=int(units_collected) if units_collected is not None else None
    )

    if not result.get("success"):
        return jsonify({"status": "error", "message": result.get("message")}), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "message": result.get("message"),
        "data": result.get("data")
    }), 200


@blood_request_api_bp.route("/api/admin/blood-requests/<req_id>/approve", methods=["POST"])
def approve_blood_request(req_id):
    """Admin approves request and matches eligible donors."""
    admin_user_id = getattr(g, "current_user_id", None)
    result = BloodRequestService.update_request_status(req_id, "APPROVED", changed_by_user_id=admin_user_id, note="Approved by Admin")
    return jsonify(result), 200 if result.get("success") else 400


@blood_request_api_bp.route("/api/admin/blood-requests/<req_id>/reject", methods=["POST"])
def reject_blood_request(req_id):
    """Admin rejects request with reason."""
    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "Rejected by Admin review")
    admin_user_id = getattr(g, "current_user_id", None)
    result = BloodRequestService.update_request_status(req_id, "REJECTED", changed_by_user_id=admin_user_id, note=reason)
    return jsonify(result), 200 if result.get("success") else 400


# -------------------------------------------------------------------------
# 8. DONOR MATCHING & DONOR RESPONSE ENDPOINTS
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/blood-requests/<req_id>/eligible-donors", methods=["GET"])
def get_eligible_donors(req_id):
    """Finds eligible voluntary donors for a request."""
    req = BloodRequestService.get_request_by_id_or_code(req_id)
    if not req:
        return jsonify({"status": "error", "message": "Blood Request not found."}), 404

    count = BloodRequestService.find_and_notify_eligible_donors(req.id)
    matches = BloodRequestDonorMatch.query.filter_by(request_id=req.id).all()

    return jsonify({
        "status": "success",
        "request_id": req.public_request_id,
        "matched_count": len(matches),
        "matches": [m.to_dict() for m in matches]
    }), 200


@blood_request_api_bp.route("/api/blood-requests/<req_id>/donor-response", methods=["POST"])
@blood_request_api_bp.route("/api/v1/blood-requests/<req_id>/donor-response", methods=["POST"])
def record_donor_response(req_id):
    """Records a voluntary donor's response (AVAILABLE / NOT_AVAILABLE)."""
    data = request.get_json(silent=True) or {}
    donor_id = data.get("donor_id", 1)
    response_status = data.get("response_status", "AVAILABLE")
    notes = data.get("notes")

    result = BloodRequestService.record_donor_response(req_id, donor_id, response_status, notes)
    return jsonify(result), 200 if result.get("success") else 400


# -------------------------------------------------------------------------
# 9. USER NOTIFICATION CENTER ENDPOINTS
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/notifications", methods=["GET"])
@blood_request_api_bp.route("/api/v1/notifications", methods=["GET"])
def get_user_notifications():
    """Retrieves user notifications with unread count."""
    user_id = getattr(g, "current_user_id", 1)
    notifications = RequestNotification.query.filter_by(user_id=user_id).order_by(RequestNotification.created_at.desc()).all()
    unread_count = RequestNotification.query.filter_by(user_id=user_id, is_read=False).count()

    return jsonify({
        "status": "success",
        "unread_count": unread_count,
        "data": [n.to_dict() for n in notifications]
    }), 200


@blood_request_api_bp.route("/api/notifications/<int:notif_id>/read", methods=["PATCH", "POST"])
def mark_notification_read(notif_id):
    """Marks a single notification as read."""
    notif = RequestNotification.query.get(notif_id)
    if notif:
        notif.is_read = True
        db.session.commit()
        return jsonify({"status": "success", "message": "Notification marked as read."}), 200
    return jsonify({"status": "error", "message": "Notification not found."}), 404


@blood_request_api_bp.route("/api/notifications/read-all", methods=["PATCH", "POST"])
def mark_all_notifications_read():
    """Marks all user notifications as read."""
    user_id = getattr(g, "current_user_id", 1)
    RequestNotification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"status": "success", "message": "All notifications marked as read."}), 200


# -------------------------------------------------------------------------
# 11. ADMIN REGISTERED DONORS & ALL DONOR RESPONSES ("I CAN DONATE")
# -------------------------------------------------------------------------
@blood_request_api_bp.route("/api/admin/registered-donors", methods=["GET"])
@blood_request_api_bp.route("/api/v1/admin/registered-donors", methods=["GET"])
def get_admin_registered_donors():
    """
    Retrieves all real registered donors for Admin Workbench.
    """
    from app.database.models.donor import DonorProfile
    from app.database.models.user import User

    donors = DonorProfile.query.filter_by(is_deleted=False).order_by(DonorProfile.created_at.desc()).all()
    results = []
    for d in donors:
        u = d.user or User.query.get(d.user_id)
        results.append({
            "donor_id": d.id,
            "user_id": d.user_id,
            "name": u.name if u else "Registered Donor",
            "email": u.email if u else "",
            "phone": u.phone if u else "",
            "blood_group": d.blood_group,
            "gender": d.gender or "N/A",
            "date_of_birth": d.date_of_birth.strftime("%Y-%m-%d") if d.date_of_birth else "",
            "city": d.city or "",
            "state": d.state or "",
            "address": d.address or "",
            "emergency_contact": d.emergency_contact or "",
            "eligibility_status": d.eligibility_status or "ELIGIBLE",
            "last_donation_date": d.last_donation_date.strftime("%Y-%m-%d") if d.last_donation_date else "None",
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else ""
        })

    return jsonify({
        "status": "success",
        "count": len(results),
        "data": results
    }), 200


@blood_request_api_bp.route("/api/admin/all-donor-responses", methods=["GET"])
@blood_request_api_bp.route("/api/v1/admin/all-donor-responses", methods=["GET"])
def get_all_donor_responses():
    """
    Retrieves all donor 'I Can Donate' offers across Emergency & Standard requests for Admin Workbench.
    """
    from app.database.models.emergency_request import EmergencyDonorResponse, EmergencyRequest
    from app.database.models.blood_request import BloodRequestDonorMatch, BloodRequest
    from app.database.models.donor import DonorProfile
    from app.database.models.user import User

    combined = []

    # 1. Emergency Donor Responses
    emg_responses = EmergencyDonorResponse.query.order_by(EmergencyDonorResponse.created_at.desc()).all()
    for er in emg_responses:
        req = EmergencyRequest.query.get(er.request_id)
        combined.append({
            "response_type": "EMERGENCY",
            "request_code": req.request_code if req else f"ER-{er.request_id}",
            "patient_name": req.patient_name if req else "N/A",
            "requester_name": req.requester_name if req else "N/A",
            "requester_phone": req.requester_phone if req else "N/A",
            "hospital_name": req.hospital_name if req else "N/A",
            "hospital_city": req.hospital_city if req else "N/A",
            "donor_name": er.donor_name,
            "donor_phone": er.donor_phone,
            "donor_blood_group": er.donor_blood_group,
            "response_status": er.response_status or "RESPONDED",
            "notes": er.response_notes or "",
            "created_at": er.created_at.strftime("%Y-%m-%d %H:%M") if er.created_at else ""
        })

    # 2. Standard Blood Request Donor Matches/Responses
    matches = BloodRequestDonorMatch.query.filter(BloodRequestDonorMatch.donor_response.in_(["AVAILABLE", "RESPONDED"])).order_by(BloodRequestDonorMatch.updated_at.desc()).all()
    for m in matches:
        req = m.request or BloodRequest.query.get(m.request_id)
        donor = m.donor or DonorProfile.query.get(m.donor_id)
        d_user = donor.user if donor else None

        combined.append({
            "response_type": "STANDARD",
            "request_code": req.public_request_id if req else f"RD-{m.request_id}",
            "patient_name": req.patient_name if req else "N/A",
            "requester_name": req.requester_name if req else "N/A",
            "requester_phone": req.requester_phone if req else "N/A",
            "hospital_name": req.hospital_name if req else "N/A",
            "hospital_city": req.hospital_city if req else "N/A",
            "donor_name": d_user.name if d_user else "Voluntary Donor",
            "donor_phone": d_user.phone if d_user else (donor.emergency_contact if donor else "N/A"),
            "donor_blood_group": donor.blood_group if donor else (req.blood_group if req else "O+"),
            "response_status": m.donor_response,
            "notes": m.donor_notes or m.match_reason or "",
            "created_at": m.responded_at.strftime("%Y-%m-%d %H:%M") if m.responded_at else (m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "")
        })

    return jsonify({
        "status": "success",
        "count": len(combined),
        "data": combined
    }), 200


@blood_request_api_bp.route("/api/blood-requests/<req_id>/donor-offers", methods=["GET"])
@blood_request_api_bp.route("/api/v1/blood-requests/<req_id>/donor-offers", methods=["GET"])
def get_donor_offers_for_request(req_id):
    """
    Retrieves list of donors who responded 'I CAN DONATE' for a specific request ID (Emergency or Standard).
    Allows requester to get donor's contact phone number and name directly.
    """
    from app.database.models.emergency_request import EmergencyDonorResponse, EmergencyRequest
    from app.database.models.blood_request import BloodRequestDonorMatch, BloodRequest
    from app.database.models.donor import DonorProfile
    from app.database.models.user import User

    offers = []

    # Check Emergency Request
    emg_req = EmergencyRequest.query.filter_by(request_code=str(req_id)).first()
    if not emg_req and str(req_id).isdigit():
        emg_req = EmergencyRequest.query.get(int(req_id))

    if emg_req:
        for resp in emg_req.responses:
            offers.append({
                "donor_name": resp.donor_name,
                "donor_phone": resp.donor_phone,
                "donor_blood_group": resp.donor_blood_group,
                "response_status": resp.response_status,
                "notes": resp.response_notes or "",
                "created_at": resp.created_at.strftime("%Y-%m-%d %H:%M") if resp.created_at else ""
            })

    # Check Standard Blood Request
    std_req = BloodRequest.query.filter_by(public_request_id=str(req_id)).first()
    if not std_req and str(req_id).isdigit():
        std_req = BloodRequest.query.get(int(req_id))

    if std_req:
        matches = BloodRequestDonorMatch.query.filter_by(request_id=std_req.id).filter(BloodRequestDonorMatch.donor_response.in_(["AVAILABLE", "RESPONDED"])).all()
        for m in matches:
            donor = m.donor or DonorProfile.query.get(m.donor_id)
            d_user = donor.user if donor else None
            offers.append({
                "donor_name": d_user.name if d_user else "Voluntary Donor",
                "donor_phone": d_user.phone if d_user else (donor.emergency_contact if donor else ""),
                "donor_blood_group": donor.blood_group if donor else std_req.blood_group,
                "donor_city": donor.city if donor else "",
                "response_status": m.donor_response,
                "notes": m.donor_notes or "",
                "created_at": m.responded_at.strftime("%Y-%m-%d %H:%M") if m.responded_at else ""
            })

    return jsonify({
        "status": "success",
        "count": len(offers),
        "data": offers
    }), 200

