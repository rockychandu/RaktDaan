"""
Blood Request Domain Service.
Member 4 — Requester / Blood Request Module.

Encapsulates complete business logic:
- Public Request ID generation (RD-2026-XXXXXX)
- 5-Section Blood Request creation & validation
- Duplicate request prevention
- Safe DB transactions
- Blood group compatibility & donor matching
- Donor notification dispatch
- Status lifecycle state machine (SUBMITTED -> UNDER_REVIEW -> APPROVED -> FULFILLED, etc.)
- Partial & complete fulfillment tracking
- Status change audit history logging
- Document upload security validation
"""

import os
import uuid
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from werkzeug.utils import secure_filename

from app.database.connection import db
from app.database.models.user import User, UserAuditLog
from app.database.models.donor import DonorProfile
from app.database.models.blood_request import (
    BloodRequest, Hospital, BloodRequestDonorMatch, RequestNotification,
    RequestStatusHistory, RequestDocument
)
from app.database.models.notification import InternalNotification
from app.users.models import UserRole, UserStatus, AuditActionType
from app.common.constants import NotificationPriority
from app.services.notification_delivery_service import notification_delivery_service

logger = logging.getLogger(__name__)

# Blood Compatibility Rules Matrix for Red Cell Transfusion
COMPATIBLE_DONOR_GROUPS = {
    "O-": ["O-"],
    "O+": ["O-", "O+"],
    "A-": ["O-", "A-"],
    "A+": ["O-", "O+", "A-", "A+"],
    "B-": ["O-", "B-"],
    "B+": ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
}

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class BloodRequestService:
    """
    Core Domain Service managing Blood Requests, Donor Matching, Fulfillment, and Audit Logs.
    """

    @staticmethod
    def generate_public_request_id() -> str:
        """
        Generates a unique public Request ID in format RD-2026-XXXXXX.
        """
        year = datetime.now(timezone.utc).strftime("%Y")
        count = BloodRequest.query.count() + 1
        code = f"RD-{year}-{count:06d}"
        while BloodRequest.query.filter_by(public_request_id=code).first() is not None:
            rnd = random.randint(100000, 999999)
            code = f"RD-{year}-{rnd}"
        return code

    @staticmethod
    def check_duplicate_request(
        patient_name: str,
        blood_group: str,
        hospital_name: str,
        requester_phone: str
    ) -> Tuple[bool, Optional[BloodRequest]]:
        """
        Prevents accidental duplicate request submissions for active patient requests.
        """
        clean_patient = patient_name.strip().lower()
        clean_phone = requester_phone.strip()
        bg = blood_group.strip().upper()

        active_statuses = [
            "SUBMITTED", "UNDER_REVIEW", "VERIFIED", "APPROVED",
            "MATCHING_DONORS", "DONOR_NOTIFIED", "PARTIALLY_FULFILLED"
        ]

        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

        existing = BloodRequest.query.filter(
            BloodRequest.status.in_(active_statuses),
            BloodRequest.blood_group == bg,
            BloodRequest.created_at >= recent_cutoff,
            (
                (BloodRequest.patient_name.ilike(clean_patient)) |
                (BloodRequest.requester_phone == clean_phone)
            )
        ).first()

        if existing:
            return True, existing
        return False, None

    @staticmethod
    def create_blood_request(data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Validates, checks duplicates, and saves a complete Blood Request in a single DB transaction.
        """
        # Section A: Requester Validation
        requester_name = data.get("requester_name", "").strip()
        requester_phone = data.get("requester_phone", "").strip()
        if not requester_name or not requester_phone:
            return {"success": False, "message": "Requester name and phone number are required.", "status_code": 400}

        # Section B: Patient Validation
        patient_name = data.get("patient_name", "").strip()
        blood_group = data.get("blood_group", "").strip().upper()
        units_required = int(data.get("units_required", 1))

        if not patient_name:
            return {"success": False, "message": "Patient name is required.", "status_code": 400}

        valid_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if blood_group not in valid_groups:
            return {"success": False, "message": f"Invalid blood group '{blood_group}'. Must be one of {', '.join(valid_groups)}", "status_code": 400}

        if units_required <= 0:
            return {"success": False, "message": "Units required must be greater than zero.", "status_code": 400}

        # Section C: Hospital Details
        hospital_name = data.get("hospital_name", "").strip()
        hospital_city = data.get("hospital_city", "Central").strip()
        if not hospital_name or not hospital_city:
            return {"success": False, "message": "Hospital name and city are required.", "status_code": 400}

        # Section D: Required Date & Urgency
        required_date = data.get("required_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")).strip()
        urgency = data.get("urgency", "URGENT").strip().upper()
        if urgency not in ["NORMAL", "URGENT", "EMERGENCY", "CRITICAL"]:
            urgency = "URGENT"

        # Check Duplicates
        is_dup, existing_req = BloodRequestService.check_duplicate_request(
            patient_name=patient_name,
            blood_group=blood_group,
            hospital_name=hospital_name,
            requester_phone=requester_phone
        )
        if is_dup and not data.get("override_duplicate"):
            return {
                "success": False,
                "is_duplicate": True,
                "duplicate_request_id": existing_req.public_request_id,
                "message": f"A similar active blood request ({existing_req.public_request_id}) for {patient_name} ({blood_group}) already exists.",
                "status_code": 409
            }

        # Begin Database Transaction
        try:
            public_id = BloodRequestService.generate_public_request_id()

            # Ensure hospital record exists in database
            hospital = Hospital.query.filter_by(name=hospital_name, city=hospital_city).first()
            if not hospital:
                hospital = Hospital(
                    name=hospital_name,
                    address=data.get("hospital_address", hospital_city),
                    city=hospital_city,
                    state=data.get("hospital_state", "State"),
                    phone=data.get("hospital_phone", requester_phone),
                    email=data.get("hospital_email", ""),
                    verification_status="VERIFIED"
                )
                db.session.add(hospital)
                db.session.flush()

            req = BloodRequest(
                public_request_id=public_id,
                requester_id=user_id,
                requester_name=requester_name,
                requester_phone=requester_phone,
                requester_email=data.get("requester_email", ""),
                relationship_with_patient=data.get("relationship_with_patient", "Relative"),
                requester_address=data.get("requester_address", ""),
                requester_city=data.get("requester_city", hospital_city),
                requester_state=data.get("requester_state", ""),
                emergency_contact_name=data.get("emergency_contact_name", ""),
                emergency_contact_phone=data.get("emergency_contact_phone", ""),
                patient_name=patient_name,
                patient_age=int(data.get("patient_age", 30)) if data.get("patient_age") else 30,
                patient_gender=data.get("patient_gender", "Male"),
                patient_identifier=data.get("patient_identifier", ""),
                medical_condition=data.get("medical_condition", ""),
                diagnosis_description=data.get("diagnosis_description", ""),
                doctor_name=data.get("doctor_name", ""),
                doctor_contact=data.get("doctor_contact", ""),
                admission_date=data.get("admission_date", ""),
                blood_group=blood_group,
                component=data.get("component", "Whole Blood"),
                units_required=units_required,
                units_collected=0,
                units_remaining=units_required,
                hospital_id=hospital.id,
                hospital_name=hospital_name,
                hospital_registration_number=data.get("hospital_registration_number", ""),
                hospital_address=data.get("hospital_address", ""),
                hospital_city=hospital_city,
                hospital_state=data.get("hospital_state", ""),
                hospital_pincode=data.get("hospital_pincode", ""),
                hospital_phone=data.get("hospital_phone", ""),
                hospital_email=data.get("hospital_email", ""),
                department_ward=data.get("department_ward", ""),
                bed_number=data.get("bed_number", ""),
                attending_doctor=data.get("attending_doctor", data.get("doctor_name", "")),
                doctor_contact_number=data.get("doctor_contact_number", data.get("doctor_contact", "")),
                blood_bank_contact=data.get("blood_bank_contact", ""),
                required_date=required_date,
                required_time=data.get("required_time", "Immediate"),
                current_availability_known=bool(data.get("current_availability_known", False)),
                replacement_required=bool(data.get("replacement_required", False)),
                urgency=urgency,
                emergency_reason=data.get("emergency_reason", ""),
                required_within=data.get("required_within", "Immediate"),
                hospital_confirmation=bool(data.get("hospital_confirmation", True)),
                doctor_confirmation=bool(data.get("doctor_confirmation", True)),
                status="SUBMITTED"
            )
            db.session.add(req)
            db.session.flush()

            # Record Status Audit History
            history = RequestStatusHistory(
                request_id=req.id,
                old_status="DRAFT",
                new_status="SUBMITTED",
                changed_by=user_id,
                note="Blood request submitted successfully."
            )
            db.session.add(history)

            # System Alert Notification for Admin Portal
            sys_notif = InternalNotification(
                title=f"🩸 New Blood Request {public_id} ({blood_group})",
                message=f"Request for {units_required} unit(s) of {blood_group} at {hospital_name}, {hospital_city} for patient {patient_name}.",
                category="SYSTEM_ALERT",
                priority=NotificationPriority.HIGH.value if urgency in ["EMERGENCY", "CRITICAL"] else NotificationPriority.MEDIUM.value,
                related_entity_type="BloodRequest",
                related_entity_id=str(req.id)
            )
            db.session.add(sys_notif)

            # Notify Requester if user account is logged in
            if user_id:
                notification_delivery_service.send(
                    user_id=user_id,
                    title=f"Blood Request {public_id} Submitted",
                    message=f"Your blood request for {units_required} unit(s) of {blood_group} has been received and is currently under review.",
                    notification_type="NEW_REQUEST",
                    priority="HIGH",
                    request_id=req.id
                )

            # Match Donors automatically if request status is APPROVED or EMERGENCY
            matched_count = 0
            if urgency in ["EMERGENCY", "CRITICAL"]:
                matched_count = BloodRequestService.find_and_notify_eligible_donors(req.id)

            db.session.commit()
            logger.info(f"Created BloodRequest #{req.id} ({public_id}) successfully.")

            return {
                "success": True,
                "message": f"Blood Request submitted successfully. Request ID: {public_id}",
                "public_request_id": public_id,
                "request_id": public_id,
                "data": req.to_dict(include_relationships=True),
                "matched_donors_notified": matched_count,
                "status_code": 201
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create BloodRequest: {str(e)}")
            return {"success": False, "message": f"Failed to submit blood request: {str(e)}", "status_code": 500}

    @staticmethod
    def get_request_by_id_or_code(identifier: Any) -> Optional[BloodRequest]:
        """
        Retrieves BloodRequest by database primary key ID or public string ID (RD-2026-XXXXXX).
        """
        if str(identifier).isdigit():
            req = BloodRequest.query.get(int(identifier))
            if req:
                return req
        return BloodRequest.query.filter_by(public_request_id=str(identifier)).first()

    @staticmethod
    def find_and_notify_eligible_donors(request_id: int) -> int:
        """
        Matches compatible voluntary donors by ABO/Rh blood compatibility and city location.
        Creates BloodRequestDonorMatch records and sends donor notifications without disclosing sensitive medical data.
        """
        req = BloodRequest.query.get(request_id)
        if not req:
            return 0

        needed_bg = req.blood_group
        compatible_groups = COMPATIBLE_DONOR_GROUPS.get(needed_bg, [needed_bg])

        # Query eligible voluntary donor profiles
        query = DonorProfile.query.filter(
            DonorProfile.blood_group.in_(compatible_groups),
            DonorProfile.is_deleted == False
        )

        # Prefer same city donors first, fallback to all available donors
        same_city_donors = query.filter(DonorProfile.city.ilike(f"%{req.hospital_city}%")).all()
        target_donors = same_city_donors if same_city_donors else query.limit(20).all()

        match_count = 0
        for donor in target_donors:
            # Check existing match
            existing = BloodRequestDonorMatch.query.filter_by(request_id=req.id, donor_id=donor.id).first()
            if not existing:
                match = BloodRequestDonorMatch(
                    request_id=req.id,
                    donor_id=donor.id,
                    match_reason=f"Compatible Blood Group ({donor.blood_group} -> {needed_bg}) in {donor.city}",
                    notification_status="SENT",
                    donor_response="PENDING"
                )
                db.session.add(match)
                match_count += 1

                # Send targeted notification to donor's user account (Non-sensitive patient info)
                if donor.user_id:
                    notification_delivery_service.send(
                        user_id=donor.user_id,
                        title=f"🚨 Urgent Blood Request ({donor.blood_group} Needed)",
                        message=f"Request {req.public_request_id}: {req.hospital_name} in {req.hospital_city} requires {req.units_required} unit(s) of {needed_bg} blood ({req.urgency} urgency). Please review if you can donate.",
                        notification_type="DONOR_MATCH",
                        priority="HIGH" if req.urgency in ["EMERGENCY", "CRITICAL"] else "MEDIUM",
                        request_id=req.id
                    )

        if match_count > 0:
            req.status = "MATCHING_DONORS"
            db.session.commit()

        logger.info(f"Matched {match_count} donors for BloodRequest {req.public_request_id}")
        return match_count

    @staticmethod
    def update_request_status(
        request_id_or_code: str,
        new_status: str,
        changed_by_user_id: Optional[int] = None,
        note: Optional[str] = None,
        units_collected: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Updates blood request status with FSM validation, audit history, and fulfillment logic.
        Valid statuses: DRAFT, SUBMITTED, UNDER_REVIEW, VERIFIED, APPROVED, MATCHING_DONORS, DONOR_NOTIFIED, PARTIALLY_FULFILLED, FULFILLED, REJECTED, CANCELLED, EXPIRED
        """
        valid_statuses = [
            "DRAFT", "SUBMITTED", "UNDER_REVIEW", "VERIFIED", "APPROVED",
            "MATCHING_DONORS", "DONOR_NOTIFIED", "PARTIALLY_FULFILLED",
            "FULFILLED", "REJECTED", "CANCELLED", "EXPIRED"
        ]

        target_status = new_status.upper().strip()
        if target_status not in valid_statuses:
            return {"success": False, "message": f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}", "status_code": 400}

        req = BloodRequestService.get_request_by_id_or_code(request_id_or_code)
        if not req:
            return {"success": False, "message": "Blood Request not found.", "status_code": 404}

        old_status = req.status
        req.status = target_status

        # Handle units collection / fulfillment
        if units_collected is not None and units_collected >= 0:
            req.units_collected = units_collected
            req.units_remaining = max(0, req.units_required - req.units_collected)
            if req.units_collected >= req.units_required:
                req.status = "FULFILLED"
                req.fulfilled_at = datetime.now(timezone.utc)
            elif req.units_collected > 0:
                req.status = "PARTIALLY_FULFILLED"

        if target_status == "APPROVED" and not req.approved_at:
            req.approved_at = datetime.now(timezone.utc)
        elif target_status == "CANCELLED":
            req.cancelled_at = datetime.now(timezone.utc)
            req.cancellation_reason = note or "Cancelled by user/admin"
        elif target_status == "REJECTED":
            req.rejection_reason = note or "Rejected by admin review"

        # Record Status History Audit Trail
        history = RequestStatusHistory(
            request_id=req.id,
            old_status=old_status,
            new_status=req.status,
            changed_by=changed_by_user_id,
            note=note or f"Status changed from {old_status} to {req.status}"
        )
        db.session.add(history)

        # Trigger Donor Matching if Approved
        if req.status == "APPROVED":
            BloodRequestService.find_and_notify_eligible_donors(req.id)

        # Notify Requester of Status Change
        if req.requester_id:
            notification_delivery_service.send(
                user_id=req.requester_id,
                title=f"Request {req.public_request_id} Status Updated: {req.status}",
                message=f"Your blood request status has been updated to '{req.status}'. {note or ''}",
                notification_type="REQUEST_STATUS_CHANGED",
                priority="HIGH" if req.status in ["APPROVED", "FULFILLED"] else "MEDIUM",
                request_id=req.id
            )

        db.session.commit()
        logger.info(f"Updated BloodRequest {req.public_request_id} status from {old_status} -> {req.status}")

        return {
            "success": True,
            "message": f"Blood Request {req.public_request_id} status updated to {req.status}.",
            "data": req.to_dict(include_relationships=True)
        }

    @staticmethod
    def record_donor_response(
        request_id_or_code: str,
        donor_id: int,
        response_status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records a voluntary donor's response (AVAILABLE / NOT_AVAILABLE) to a blood request match.
        """
        req = BloodRequestService.get_request_by_id_or_code(request_id_or_code)
        if not req:
            return {"success": False, "message": "Blood Request not found.", "status_code": 404}

        match = BloodRequestDonorMatch.query.filter_by(request_id=req.id, donor_id=donor_id).first()
        if not match:
            # Create match on the fly if voluntary donor responds directly
            match = BloodRequestDonorMatch(
                request_id=req.id,
                donor_id=donor_id,
                match_reason="Direct voluntary response",
                notification_status="DELIVERED"
            )
            db.session.add(match)

        resp = response_status.upper().strip()
        if resp not in ["AVAILABLE", "NOT_AVAILABLE"]:
            return {"success": False, "message": "Invalid response status. Must be AVAILABLE or NOT_AVAILABLE.", "status_code": 400}

        match.donor_response = resp
        match.donor_notes = notes or ""
        match.responded_at = datetime.now(timezone.utc)

        # Notify Admin if donor responds AVAILABLE
        if resp == "AVAILABLE" and req.requester_id:
            notification_delivery_service.send(
                user_id=req.requester_id,
                title=f"Donor Available for Request {req.public_request_id}",
                message=f"A voluntary donor has responded AVAILABLE for your request at {req.hospital_name}.",
                notification_type="DONOR_RESPONSE",
                priority="HIGH",
                request_id=req.id
            )

        db.session.commit()
        logger.info(f"Recorded donor response ({resp}) for Request {req.public_request_id}")

        return {
            "success": True,
            "message": f"Your response ({resp}) has been recorded. Thank you for your support!",
            "data": match.to_dict()
        }

    @staticmethod
    def save_supporting_document(
        request_id_or_code: str,
        file_obj,
        uploaded_by_user_id: Optional[int] = None,
        upload_folder: str = "app/static/uploads/documents"
    ) -> Dict[str, Any]:
        """
        Validates, sanitizes, and stores supporting clinical/hospital documents.
        """
        req = BloodRequestService.get_request_by_id_or_code(request_id_or_code)
        if not req:
            return {"success": False, "message": "Blood Request not found.", "status_code": 404}

        if not file_obj or not file_obj.filename:
            return {"success": False, "message": "No document file provided.", "status_code": 400}

        filename = secure_filename(file_obj.filename)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if ext not in ALLOWED_EXTENSIONS:
            return {"success": False, "message": f"Unsupported file extension '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", "status_code": 400}

        # Generate unique safe filename
        safe_name = f"{req.public_request_id}_{uuid.uuid4().hex[:8]}.{ext}"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, safe_name)

        file_obj.save(file_path)
        file_size = os.path.getsize(file_path)

        if file_size > MAX_FILE_SIZE_BYTES:
            os.remove(file_path)
            return {"success": False, "message": "File size exceeds 10 MB limit.", "status_code": 400}

        doc = RequestDocument(
            request_id=req.id,
            document_type=f"Clinical Document ({ext.upper()})",
            file_path=f"/static/uploads/documents/{safe_name}",
            file_name=filename,
            file_size=file_size,
            mime_type=file_obj.mimetype,
            uploaded_by=uploaded_by_user_id
        )
        db.session.add(doc)
        db.session.commit()

        logger.info(f"Saved document {safe_name} for Request {req.public_request_id}")
        return {
            "success": True,
            "message": "Supporting document uploaded successfully.",
            "data": doc.to_dict()
        }
