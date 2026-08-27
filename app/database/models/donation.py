"""
Donation & Medical Screening Database Models (Member 3).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin
from app.common.constants import DonationStatus, DonationType


class DonationRecord(db.Model, BaseModelMixin):
    """
    Donation Record table tracking donor donation events and status lifecycle.
    """
    __tablename__ = "donation_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donation_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    donation_type = db.Column(db.String(50), nullable=False, default=DonationType.WHOLE_BLOOD.value)
    donation_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    volume_ml = db.Column(db.Integer, default=450, nullable=False)
    collection_center = db.Column(db.String(150), nullable=False, default="Central RaktDaan Blood Bank")
    staff_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    screening_status = db.Column(db.String(30), default="PENDING", nullable=False) # PENDING, PASSED, FAILED
    donation_status = db.Column(db.String(30), default=DonationStatus.REGISTERED.value, nullable=False, index=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    donor_profile = db.relationship("DonorProfile", backref=db.backref("donation_records", lazy=True, cascade="all, delete-orphan"))
    screening = db.relationship("DonationScreening", backref="donation_record", uselist=False, cascade="all, delete-orphan")
    blood_bags = db.relationship("BloodBag", backref="donation_record", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "donation_code": self.donation_code,
            "donor_id": self.donor_id,
            "donor_name": self.donor_profile.user.name if (self.donor_profile and self.donor_profile.user) else None,
            "blood_group": self.blood_group,
            "donation_type": self.donation_type,
            "donation_date": self.donation_date.isoformat() if self.donation_date else None,
            "volume_ml": self.volume_ml,
            "collection_center": self.collection_center,
            "staff_user_id": self.staff_user_id,
            "screening_status": self.screening_status,
            "donation_status": self.donation_status,
            "cancellation_reason": self.cancellation_reason,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<DonationRecord id={self.id} code='{self.donation_code}' status='{self.donation_status}'>"


class DonationScreening(db.Model, BaseModelMixin):
    """
    Detailed Medical Vitals & Health Screening for Donation Registration.
    """
    __tablename__ = "donation_screenings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("donation_records.id", ondelete="CASCADE"), unique=True, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    hemoglobin_level = db.Column(db.Float, nullable=False)
    blood_pressure_sys = db.Column(db.Integer, nullable=False)
    blood_pressure_dia = db.Column(db.Integer, nullable=False)
    pulse_rate = db.Column(db.Integer, nullable=False)
    temp_celsius = db.Column(db.Float, default=36.5, nullable=False)
    has_chronic_illness = db.Column(db.Boolean, default=False, nullable=False)
    is_on_medication = db.Column(db.Boolean, default=False, nullable=False)
    is_passed = db.Column(db.Boolean, nullable=False)
    screening_notes = db.Column(db.Text, nullable=True)
    evaluated_by_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "donation_id": self.donation_id,
            "weight_kg": self.weight_kg,
            "hemoglobin_level": self.hemoglobin_level,
            "blood_pressure_sys": self.blood_pressure_sys,
            "blood_pressure_dia": self.blood_pressure_dia,
            "pulse_rate": self.pulse_rate,
            "temp_celsius": self.temp_celsius,
            "has_chronic_illness": self.has_chronic_illness,
            "is_on_medication": self.is_on_medication,
            "is_passed": self.is_passed,
            "screening_notes": self.screening_notes,
            "evaluated_by_staff_id": self.evaluated_by_staff_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
