"""
Emergency Request & Donor Response Domain Service.
Handles persistent DB storage, request ID generation, status FSM transitions,
donor response tracking, and search/filter queries for Admin and Donor portals.
"""

import random
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.database.connection import db
from app.database.models.emergency_request import EmergencyRequest, EmergencyDonorResponse
from app.database.models.notification import InternalNotification
from app.common.constants import NotificationCategory, NotificationPriority

logger = logging.getLogger(__name__)


class EmergencyRequestService:
    """
    Domain service for Emergency Request management.
    """

    @staticmethod
    def generate_request_code() -> str:
        """Generates unique Request ID in format ER-2026-XXXXXX."""
        yr = datetime.utcnow().strftime("%Y")
        rnd = random.randint(100000, 999999)
        code = f"ER-{yr}-{rnd}"
        while EmergencyRequest.query.filter_by(request_code=code).first() is not None:
            rnd = random.randint(100000, 999999)
            code = f"ER-{yr}-{rnd}"
        return code

    @staticmethod
    def create_request(data: Dict[str, Any], user_id: Optional[int] = None) -> EmergencyRequest:
        """
        Creates and saves a new Emergency Blood Request persistently in the database.
        """
        code = EmergencyRequestService.generate_request_code()
        
        req = EmergencyRequest(
            request_code=code,
            requester_id=user_id,
            requester_name=data.get("requester_name", "Emergency Requester"),
            requester_phone=data.get("requester_phone", data.get("contact_number", "9876543210")),
            requester_email=data.get("requester_email", ""),
            patient_name=data.get("patient_name", "Emergency Patient"),
            patient_age=int(data.get("patient_age", 30)) if data.get("patient_age") else 30,
            blood_group=data.get("blood_group", "O+").upper(),
            units_required=int(data.get("units_required", 1)),
            hospital_name=data.get("hospital_name", "Central Hospital"),
            hospital_address=data.get("hospital_address", data.get("hospital_location", "")),
            hospital_city=data.get("hospital_city", "Central"),
            urgency_level=data.get("urgency_level", "HIGH").upper(),
            required_datetime=str(data.get("required_datetime", "Immediate")),
            additional_reason=data.get("additional_reason", data.get("message", "")),
            status="PENDING"
        )
        db.session.add(req)

        # Sync with Member 4 BloodRequest table so it appears in Admin Portal Blood Requests Tab
        try:
            from app.database.models.blood_request import BloodRequest, RequestStatusHistory
            br = BloodRequest(
                public_request_id=code,
                requester_id=user_id,
                requester_name=req.requester_name,
                requester_phone=req.requester_phone,
                requester_email=req.requester_email or "",
                relationship_with_patient="Emergency Contact",
                patient_name=req.patient_name,
                patient_age=req.patient_age or 30,
                patient_gender="Male",
                blood_group=req.blood_group,
                component="Whole Blood",
                units_required=req.units_required,
                units_collected=0,
                units_remaining=req.units_required,
                hospital_name=req.hospital_name,
                hospital_address=req.hospital_address or "",
                hospital_city=req.hospital_city or "Central",
                required_date=datetime.utcnow().strftime("%Y-%m-%d"),
                required_time=req.required_datetime or "Immediate",
                urgency=req.urgency_level,
                emergency_reason=req.additional_reason or "Emergency Dispatch Request",
                status="SUBMITTED"
            )
            db.session.add(br)
            db.session.flush()

            history = RequestStatusHistory(
                request_id=br.id,
                old_status="DRAFT",
                new_status="SUBMITTED",
                changed_by=user_id,
                note="Emergency blood request submitted."
            )
            db.session.add(history)
        except Exception as sync_err:
            logger.warning(f"Failed to sync BloodRequest record: {sync_err}")

        db.session.commit()

        # Log system alert notification
        try:
            notif = InternalNotification(
                title=f"🚨 Emergency Request {code} ({req.blood_group})",
                message=f"Urgent request for {req.units_required} unit(s) of {req.blood_group} at {req.hospital_name} by {req.requester_name}.",
                category="SYSTEM_ALERT",
                priority=NotificationPriority.HIGH.value
            )
            db.session.add(notif)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log notification: {e}")

        logger.info(f"Created persistent EmergencyRequest #{req.id} ({code})")
        return req

    @staticmethod
    def get_all_requests_admin(
        blood_group: Optional[str] = None,
        status: Optional[str] = None,
        urgency: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[EmergencyRequest]:
        """
        Retrieves emergency requests for Admin Portal with optional search/filtering.
        """
        query = EmergencyRequest.query

        if blood_group and blood_group.strip():
            query = query.filter(EmergencyRequest.blood_group == blood_group.strip().upper())

        if status and status.strip():
            query = query.filter(EmergencyRequest.status == status.strip().upper())

        if urgency and urgency.strip():
            query = query.filter(EmergencyRequest.urgency_level == urgency.strip().upper())

        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            query = query.filter(
                (EmergencyRequest.request_code.ilike(q)) |
                (EmergencyRequest.requester_name.ilike(q)) |
                (EmergencyRequest.patient_name.ilike(q)) |
                (EmergencyRequest.hospital_name.ilike(q))
            )

        return query.order_by(EmergencyRequest.created_at.desc()).all()

    @staticmethod
    def get_active_requests_donor(blood_group: Optional[str] = None) -> List[EmergencyRequest]:
        """
        Retrieves active emergency requests for Donors.
        Filters by status IN ('PENDING', 'APPROVED', 'ACTIVE').
        """
        query = EmergencyRequest.query.filter(
            EmergencyRequest.status.in_(["PENDING", "APPROVED", "ACTIVE"])
        )

        if blood_group and blood_group.strip():
            query = query.filter(EmergencyRequest.blood_group == blood_group.strip().upper())

        return query.order_by(EmergencyRequest.created_at.desc()).all()

    @staticmethod
    def get_by_code_or_id(identifier: str) -> Optional[EmergencyRequest]:
        """Finds request by primary key ID or string code."""
        if str(identifier).isdigit():
            req = EmergencyRequest.query.get(int(identifier))
            if req:
                return req
        return EmergencyRequest.query.filter_by(request_code=str(identifier)).first()

    @staticmethod
    def update_request_status(request_id_or_code: str, new_status: str) -> Dict[str, Any]:
        """
        Updates the status of an emergency request with validation.
        Valid statuses: PENDING, APPROVED, ACTIVE, FULFILLED, REJECTED, CANCELLED, EXPIRED.
        """
        allowed = ["PENDING", "APPROVED", "ACTIVE", "FULFILLED", "REJECTED", "CANCELLED", "EXPIRED"]
        target_status = new_status.upper().strip()
        
        if target_status not in allowed:
            return {"success": False, "message": f"Invalid status '{new_status}'. Allowed: {', '.join(allowed)}"}

        req = EmergencyRequestService.get_by_code_or_id(request_id_or_code)
        if not req:
            return {"success": False, "message": "Emergency Request not found."}

        req.status = target_status
        req.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Updated EmergencyRequest {req.request_code} status to '{target_status}'")
        return {
            "success": True,
            "message": f"Request {req.request_code} status updated to {target_status}.",
            "request": req.to_dict()
        }

    @staticmethod
    def add_donor_response(
        request_id_or_code: str,
        donor_id: Optional[int],
        donor_name: str,
        donor_phone: str,
        donor_blood_group: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records a donor's response ('I CAN DONATE') to an emergency request.
        """
        req = EmergencyRequestService.get_by_code_or_id(request_id_or_code)
        if not req:
            return {"success": False, "message": "Emergency Request not found."}

        # Check existing response by donor
        if donor_id:
            existing = EmergencyDonorResponse.query.filter_by(request_id=req.id, donor_id=donor_id).first()
            if existing:
                return {
                    "success": True,
                    "message": "You have already responded to this emergency request.",
                    "response": existing.to_dict()
                }

        resp = EmergencyDonorResponse(
            request_id=req.id,
            donor_id=donor_id,
            donor_name=donor_name,
            donor_phone=donor_phone,
            donor_blood_group=donor_blood_group.upper(),
            response_status="RESPONDED",
            response_notes=notes or "Pledged voluntary donor response."
        )
        db.session.add(resp)
        db.session.commit()

        logger.info(f"Recorded donor response from {donor_name} for EmergencyRequest {req.request_code}")
        return {
            "success": True,
            "message": f"Thank you {donor_name}! Your response to emergency request {req.request_code} has been recorded.",
            "response": resp.to_dict()
        }
