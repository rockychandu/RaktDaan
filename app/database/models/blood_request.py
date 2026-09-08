"""
Blood Request, Hospital, Donor Matching, Notification, Status History, and Document Models.
Member 4 — Requester / Blood Request Module.
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class Hospital(db.Model, BaseModelMixin):
    """
    Hospital Directory Entity for associated blood request locations.
    """
    __tablename__ = "hospitals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    registration_number = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    verification_status = db.Column(db.String(30), nullable=False, default="VERIFIED", index=True)

    requests = db.relationship("BloodRequest", backref="hospital", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "registration_number": self.registration_number or "",
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode or "",
            "phone": self.phone,
            "email": self.email or "",
            "department": self.department or "",
            "verification_status": self.verification_status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class BloodRequest(db.Model, BaseModelMixin):
    """
    Comprehensive Blood Request Entity managing requester workflow, patient clinical info,
    hospital details, urgency, and status lifecycle.
    """
    __tablename__ = "blood_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_request_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Requester Information
    requester_name = db.Column(db.String(120), nullable=False)
    requester_phone = db.Column(db.String(30), nullable=False)
    requester_email = db.Column(db.String(150), nullable=True)
    relationship_with_patient = db.Column(db.String(50), nullable=False, default="Relative")
    requester_address = db.Column(db.String(300), nullable=True)
    requester_city = db.Column(db.String(100), nullable=True)
    requester_state = db.Column(db.String(100), nullable=True)
    emergency_contact_name = db.Column(db.String(120), nullable=True)
    emergency_contact_phone = db.Column(db.String(30), nullable=True)

    # Patient Details
    patient_name = db.Column(db.String(120), nullable=False)
    patient_age = db.Column(db.Integer, nullable=False, default=30)
    patient_gender = db.Column(db.String(20), nullable=False, default="Male")
    patient_identifier = db.Column(db.String(100), nullable=True)
    medical_condition = db.Column(db.Text, nullable=True)
    diagnosis_description = db.Column(db.Text, nullable=True)
    doctor_name = db.Column(db.String(120), nullable=True)
    doctor_contact = db.Column(db.String(30), nullable=True)
    admission_date = db.Column(db.String(30), nullable=True)

    # Blood Requirement
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    component = db.Column(db.String(50), nullable=False, default="Whole Blood")
    units_required = db.Column(db.Integer, nullable=False, default=1)
    units_collected = db.Column(db.Integer, nullable=False, default=0)
    units_remaining = db.Column(db.Integer, nullable=False, default=1)

    # Hospital Details
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    hospital_name = db.Column(db.String(200), nullable=False, index=True)
    hospital_registration_number = db.Column(db.String(100), nullable=True)
    hospital_address = db.Column(db.String(300), nullable=True)
    hospital_city = db.Column(db.String(100), nullable=False, index=True)
    hospital_state = db.Column(db.String(100), nullable=True)
    hospital_pincode = db.Column(db.String(20), nullable=True)
    hospital_phone = db.Column(db.String(30), nullable=True)
    hospital_email = db.Column(db.String(150), nullable=True)
    department_ward = db.Column(db.String(100), nullable=True)
    bed_number = db.Column(db.String(50), nullable=True)
    attending_doctor = db.Column(db.String(120), nullable=True)
    doctor_contact_number = db.Column(db.String(30), nullable=True)
    blood_bank_contact = db.Column(db.String(30), nullable=True)
    hospital_verification_status = db.Column(db.String(30), default="VERIFIED")

    # Schedule & Urgency
    required_date = db.Column(db.String(30), nullable=False)
    required_time = db.Column(db.String(30), nullable=True, default="Immediate")
    current_availability_known = db.Column(db.Boolean, default=False)
    replacement_required = db.Column(db.Boolean, default=False)
    urgency = db.Column(db.String(20), nullable=False, default="URGENT", index=True) # NORMAL, URGENT, EMERGENCY, CRITICAL
    emergency_reason = db.Column(db.Text, nullable=True)
    required_within = db.Column(db.String(50), nullable=True)
    hospital_confirmation = db.Column(db.Boolean, default=True)
    doctor_confirmation = db.Column(db.Boolean, default=True)

    # Status Workflow Lifecycle
    # Statuses: DRAFT, SUBMITTED, UNDER_REVIEW, VERIFIED, APPROVED, MATCHING_DONORS, DONOR_NOTIFIED, PARTIALLY_FULFILLED, FULFILLED, REJECTED, CANCELLED, EXPIRED
    status = db.Column(db.String(30), nullable=False, default="SUBMITTED", index=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    internal_notes = db.Column(db.Text, nullable=True)

    # Timestamps
    approved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    fulfilled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    user = db.relationship("User", backref="blood_requests")
    donor_matches = db.relationship("BloodRequestDonorMatch", backref="request", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship("RequestNotification", backref="request", lazy=True, cascade="all, delete-orphan")
    status_history = db.relationship("RequestStatusHistory", backref="request", lazy=True, cascade="all, delete-orphan")
    documents = db.relationship("RequestDocument", backref="request", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_relationships=False):
        data = {
            "id": self.id,
            "public_request_id": self.public_request_id,
            "request_id": self.public_request_id,
            "requester_id": self.requester_id,
            "requester_name": self.requester_name,
            "requester_phone": self.requester_phone,
            "requester_email": self.requester_email or "",
            "relationship_with_patient": self.relationship_with_patient,
            "requester_address": self.requester_address or "",
            "requester_city": self.requester_city or "",
            "requester_state": self.requester_state or "",
            "emergency_contact_name": self.emergency_contact_name or "",
            "emergency_contact_phone": self.emergency_contact_phone or "",
            "patient_name": self.patient_name,
            "patient_age": self.patient_age,
            "patient_gender": self.patient_gender,
            "patient_identifier": self.patient_identifier or "",
            "medical_condition": self.medical_condition or "",
            "diagnosis_description": self.diagnosis_description or "",
            "doctor_name": self.doctor_name or "",
            "doctor_contact": self.doctor_contact or "",
            "admission_date": self.admission_date or "",
            "blood_group": self.blood_group,
            "component": self.component,
            "units_required": self.units_required,
            "units_collected": self.units_collected,
            "units_remaining": self.units_remaining,
            "hospital_id": self.hospital_id,
            "hospital_name": self.hospital_name,
            "hospital_registration_number": self.hospital_registration_number or "",
            "hospital_address": self.hospital_address or "",
            "hospital_city": self.hospital_city,
            "hospital_state": self.hospital_state or "",
            "hospital_pincode": self.hospital_pincode or "",
            "hospital_phone": self.hospital_phone or "",
            "hospital_email": self.hospital_email or "",
            "department_ward": self.department_ward or "",
            "bed_number": self.bed_number or "",
            "attending_doctor": self.attending_doctor or "",
            "doctor_contact_number": self.doctor_contact_number or "",
            "blood_bank_contact": self.blood_bank_contact or "",
            "hospital_verification_status": self.hospital_verification_status,
            "required_date": self.required_date,
            "required_time": self.required_time or "Immediate",
            "current_availability_known": self.current_availability_known,
            "replacement_required": self.replacement_required,
            "urgency": self.urgency,
            "emergency_reason": self.emergency_reason or "",
            "required_within": self.required_within or "",
            "hospital_confirmation": self.hospital_confirmation,
            "doctor_confirmation": self.doctor_confirmation,
            "status": self.status,
            "cancellation_reason": self.cancellation_reason or "",
            "rejection_reason": self.rejection_reason or "",
            "internal_notes": self.internal_notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "fulfilled_at": self.fulfilled_at.isoformat() if self.fulfilled_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
        }
        if include_relationships:
            data["donor_matches"] = [m.to_dict() for m in self.donor_matches]
            data["status_history"] = [h.to_dict() for h in self.status_history]
            data["documents"] = [d.to_dict() for d in self.documents]
        return data


class BloodRequestDonorMatch(db.Model, BaseModelMixin):
    """
    Entity associating eligible voluntary donors to a specific blood request.
    """
    __tablename__ = "blood_request_donor_matches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    match_reason = db.Column(db.String(255), nullable=False)
    notification_status = db.Column(db.String(30), default="SENT", index=True) # PENDING, SENT, DELIVERED, FAILED
    donor_response = db.Column(db.String(30), default="PENDING", index=True) # PENDING, AVAILABLE, NOT_AVAILABLE
    donor_notes = db.Column(db.Text, nullable=True)
    responded_at = db.Column(db.DateTime(timezone=True), nullable=True)

    donor = db.relationship("DonorProfile", backref="matched_requests")

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "donor_id": self.donor_id,
            "donor_name": self.donor.user.name if (self.donor and self.donor.user) else "Voluntary Donor",
            "donor_blood_group": self.donor.blood_group if self.donor else "",
            "donor_city": self.donor.city if self.donor else "",
            "match_reason": self.match_reason,
            "notification_status": self.notification_status,
            "donor_response": self.donor_response,
            "donor_notes": self.donor_notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None
        }


class RequestNotification(db.Model, BaseModelMixin):
    """
    Targeted Notification Entity for Requester, Donor, and Admin alerts.
    """
    __tablename__ = "request_notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    request_id = db.Column(db.Integer, db.ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=True, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="MEDIUM", index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", backref="request_notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "priority": self.priority,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }


class RequestStatusHistory(db.Model, BaseModelMixin):
    """
    Audit Trail logging state transitions for Blood Requests.
    """
    __tablename__ = "request_status_histories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = db.Column(db.String(30), nullable=False)
    new_status = db.Column(db.String(30), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note = db.Column(db.Text, nullable=True)

    changer = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changer.name if self.changer else "System",
            "note": self.note or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RequestDocument(db.Model, BaseModelMixin):
    """
    Supporting Clinical & Hospital Verification Document Storage Entity.
    """
    __tablename__ = "request_documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False, default=0)
    mime_type = db.Column(db.String(100), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "mime_type": self.mime_type or "",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
