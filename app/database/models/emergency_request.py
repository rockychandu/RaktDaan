"""
Emergency Blood Request & Donor Response Models.
Persistently manages emergency requests submitted from Home Page or Portals,
along with voluntary donor responses and admin state transitions.
"""

from datetime import datetime
from app.database.connection import db


class EmergencyRequest(db.Model):
    """
    Persistently stores Emergency Blood Requests submitted from Home Page, Donor Portal, or Hospitals.
    """
    __tablename__ = "emergency_requests"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    
    # Requester Details
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    requester_name = db.Column(db.String(120), nullable=False)
    requester_phone = db.Column(db.String(30), nullable=False)
    requester_email = db.Column(db.String(120), nullable=True)

    # Patient & Requirement Details
    patient_name = db.Column(db.String(120), nullable=False)
    patient_age = db.Column(db.Integer, nullable=True)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    units_required = db.Column(db.Integer, nullable=False, default=1)
    
    # Hospital Details
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_address = db.Column(db.String(300), nullable=True)
    hospital_city = db.Column(db.String(100), nullable=True)
    
    # Priority & Schedule
    urgency_level = db.Column(db.String(20), nullable=False, default="HIGH", index=True) # STAT, HIGH, MEDIUM, LOW
    required_datetime = db.Column(db.String(50), nullable=True)
    additional_reason = db.Column(db.Text, nullable=True)
    
    # Status Workflow: PENDING, APPROVED, ACTIVE, FULFILLED, REJECTED, CANCELLED, EXPIRED
    status = db.Column(db.String(30), nullable=False, default="PENDING", index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to donor responses
    responses = db.relationship("EmergencyDonorResponse", backref="request", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_code,
            "request_code": self.request_code,
            "requester_id": f"USR{self.requester_id:04d}" if self.requester_id else "GUEST",
            "requester_name": self.requester_name,
            "requester_phone": self.requester_phone,
            "requester_email": self.requester_email or "",
            "patient_name": self.patient_name,
            "patient_age": self.patient_age or 0,
            "blood_group": self.blood_group,
            "units_required": self.units_required,
            "hospital_name": self.hospital_name,
            "hospital_address": self.hospital_address or "",
            "hospital_city": self.hospital_city or "Central",
            "urgency_level": self.urgency_level,
            "required_datetime": self.required_datetime or "Immediate",
            "additional_reason": self.additional_reason or "",
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
            "donor_responses_count": len(self.responses),
            "donor_responses": [r.to_dict() for r in self.responses]
        }


class EmergencyDonorResponse(db.Model):
    """
    Tracks Donor responses ('I CAN DONATE') to active emergency blood requests.
    """
    __tablename__ = "emergency_donor_responses"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey("emergency_requests.id", ondelete="CASCADE"), nullable=False)
    donor_id = db.Column(db.Integer, nullable=True)
    donor_name = db.Column(db.String(120), nullable=False)
    donor_phone = db.Column(db.String(30), nullable=False)
    donor_blood_group = db.Column(db.String(10), nullable=False)
    response_status = db.Column(db.String(30), default="RESPONDED") # RESPONDED, CONFIRMED, FULFILLED, CANCELLED
    response_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "donor_id": self.donor_id,
            "donor_name": self.donor_name,
            "donor_phone": self.donor_phone,
            "donor_blood_group": self.donor_blood_group,
            "response_status": self.response_status,
            "response_notes": self.response_notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else ""
        }
