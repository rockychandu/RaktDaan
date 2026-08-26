from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin
from app.users.models import BloodGroup, Gender, EligibilityStatus
from app.security.field_encryption import FieldEncryptor

class DonorProfile(db.Model, BaseModelMixin):
    """
    Donor Profile Entity linked 1-to-1 with User table.
    """
    __tablename__ = "donor_profiles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    address_encrypted = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False, index=True)
    emergency_contact_encrypted = db.Column(db.String(255), nullable=False)
    eligibility_status = db.Column(db.String(30), nullable=False, default=EligibilityStatus.ELIGIBLE.value, index=True)
    last_donation_date = db.Column(db.Date, nullable=True)

    # Relationships
    medical_histories = db.relationship("DonorMedicalHistory", backref="donor_profile", cascade="all, delete-orphan")
    emergency_contacts = db.relationship("DonorEmergencyContact", backref="donor_profile", cascade="all, delete-orphan")
    preferences = db.relationship("DonorPreference", backref="donor_profile", uselist=False, cascade="all, delete-orphan")

    @property
    def address(self) -> str:
        return FieldEncryptor.decrypt(self.address_encrypted)

    @address.setter
    def address(self, value: str):
        self.address_encrypted = FieldEncryptor.encrypt(value)

    @property
    def emergency_contact(self) -> str:
        return FieldEncryptor.decrypt(self.emergency_contact_encrypted)

    @emergency_contact.setter
    def emergency_contact(self, value: str):
        self.emergency_contact_encrypted = FieldEncryptor.encrypt(value)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "emergency_contact": self.emergency_contact,
            "eligibility_status": self.eligibility_status,
            "last_donation_date": self.last_donation_date.isoformat() if self.last_donation_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<DonorProfile id={self.id} user_id={self.user_id} blood_group='{self.blood_group}'>"


class DonorMedicalHistory(db.Model, BaseModelMixin):
    """
    Donor Medical Questionnaire & Health Check History Table.
    """
    __tablename__ = "donor_medical_histories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_profile_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    weight_kg = db.Column(db.Float, nullable=False)
    hemoglobin_level = db.Column(db.Float, nullable=True)
    blood_pressure_sys = db.Column(db.Integer, nullable=True)
    blood_pressure_dia = db.Column(db.Integer, nullable=True)
    pulse_rate = db.Column(db.Integer, nullable=True)
    has_chronic_illness = db.Column(db.Boolean, default=False, nullable=False)
    is_on_medication = db.Column(db.Boolean, default=False, nullable=False)
    medical_notes = db.Column(db.Text, nullable=True)


class DonorEligibility(db.Model, BaseModelMixin):
    """
    Donor Eligibility Rule Evaluation Engine Log Table.
    """
    __tablename__ = "donor_eligibilities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_profile_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default=EligibilityStatus.ELIGIBLE.value)
    reason = db.Column(db.String(255), nullable=True)
    eligible_after_date = db.Column(db.Date, nullable=True)


class DonorEmergencyContact(db.Model, BaseModelMixin):
    """
    Secondary Emergency Contacts Table for Donors.
    """
    __tablename__ = "donor_emergency_contacts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_profile_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    phone_encrypted = db.Column(db.String(255), nullable=False)


class DonorPreference(db.Model, BaseModelMixin):
    """
    Donor Notification & Emergency Alert Preferences Table.
    """
    __tablename__ = "donor_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_profile_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    allow_emergency_sms = db.Column(db.Boolean, default=True, nullable=False)
    allow_email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    preferred_donation_center = db.Column(db.String(100), nullable=True)
