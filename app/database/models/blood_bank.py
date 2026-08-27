"""
Blood Bank & Inventory Core Database Models (Member 4).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin
from app.common.constants import BloodBagStatus, ComponentType


class BloodInventory(db.Model, BaseModelMixin):
    """
    Blood Bank Aggregate Inventory Table.
    Tracks total available, reserved, and expired units by blood group.
    """
    __tablename__ = "blood_inventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blood_group = db.Column(db.String(10), unique=True, nullable=False, index=True)
    units_available = db.Column(db.Integer, default=0, nullable=False)
    units_reserved = db.Column(db.Integer, default=0, nullable=False)
    units_expired = db.Column(db.Integer, default=0, nullable=False)
    last_updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "blood_group": self.blood_group,
            "units_available": self.units_available,
            "units_reserved": self.units_reserved,
            "units_expired": self.units_expired,
            "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at else None
        }


class BloodBag(db.Model, BaseModelMixin):
    """
    Individual Blood Bag Tracking Table with Full Traceability.
    """
    __tablename__ = "blood_bags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bag_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("donation_records.id", ondelete="SET NULL"), nullable=True, index=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    component_type = db.Column(db.String(50), nullable=False, default=ComponentType.WHOLE_BLOOD.value, index=True)
    volume_ml = db.Column(db.Integer, default=450, nullable=False)
    collection_date = db.Column(db.Date, nullable=False, index=True)
    processing_date = db.Column(db.Date, nullable=True)
    testing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    storage_unit_id = db.Column(db.Integer, db.ForeignKey("storage_units.id", ondelete="SET NULL"), nullable=True)
    shelf_position = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default=BloodBagStatus.COLLECTED.value, nullable=False, index=True)
    quality_status = db.Column(db.String(30), default="PASSED", nullable=False) # PASSED, FAILED, UNTESTED
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    donor_profile = db.relationship("DonorProfile", backref="blood_bags")
    status_logs = db.relationship("BloodBagStatusLog", backref="blood_bag", cascade="all, delete-orphan")
    quarantine_records = db.relationship("QuarantineRecord", backref="blood_bag", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "bag_code": self.bag_code,
            "donation_id": self.donation_id,
            "donor_id": self.donor_id,
            "donor_name": self.donor_profile.user.name if (self.donor_profile and self.donor_profile.user) else None,
            "blood_group": self.blood_group,
            "component_type": self.component_type,
            "volume_ml": self.volume_ml,
            "collection_date": self.collection_date.isoformat() if self.collection_date else None,
            "processing_date": self.processing_date.isoformat() if self.processing_date else None,
            "testing_date": self.testing_date.isoformat() if self.testing_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "storage_unit_id": self.storage_unit_id,
            "storage_unit_name": self.storage_unit.name if self.storage_unit else None,
            "shelf_position": self.shelf_position,
            "status": self.status,
            "quality_status": self.quality_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<BloodBag id={self.id} code='{self.bag_code}' blood_group='{self.blood_group}' status='{self.status}'>"


class BloodDrive(db.Model, BaseModelMixin):
    """
    Blood Donation Camps and Drives Table.
    """
    __tablename__ = "blood_drives"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    location_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    organizer_contact = db.Column(db.String(100), nullable=False)


class BloodRequest(db.Model, BaseModelMixin):
    """
    Blood Request Table for Hospitals and Patients.
    """
    __tablename__ = "blood_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    requester_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    units_requested = db.Column(db.Integer, nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default="PENDING", nullable=False)


class RequestFulfillment(db.Model, BaseModelMixin):
    """
    Blood Request Fulfillment Audit Table.
    """
    __tablename__ = "request_fulfillments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey("blood_requests.id"), nullable=False)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id"), nullable=False)
    fulfilled_by_admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    fulfilled_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BloodCompatibilityMatrix(db.Model, BaseModelMixin):
    """
    Universal Blood Group Compatibility Reference Matrix.
    """
    __tablename__ = "blood_compatibility_matrices"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipient_blood_group = db.Column(db.String(10), nullable=False, index=True)
    compatible_donor_blood_group = db.Column(db.String(10), nullable=False, index=True)
