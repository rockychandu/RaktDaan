from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin

class BloodInventory(db.Model, BaseModelMixin):
    """
    Blood Bank Aggregate Inventory Table. (For Member 4)
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
    Individual Blood Bag Tracking Table. (For Member 3 & Member 4)
    """
    __tablename__ = "blood_bags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bag_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="SET NULL"), nullable=True)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    volume_ml = db.Column(db.Integer, default=450, nullable=False)
    collection_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default="AVAILABLE", nullable=False) # AVAILABLE, RESERVED, USED, EXPIRED, DISCARDED


class BloodDrive(db.Model, BaseModelMixin):
    """
    Blood Donation Camps and Drives Table. (For Member 3)
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
    Blood Request Table for Hospitals and Patients. (For Member 5)
    """
    __tablename__ = "blood_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    requester_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    units_requested = db.Column(db.Integer, nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default="PENDING", nullable=False) # PENDING, APPROVED, REJECTED, FULFILLED


class RequestFulfillment(db.Model, BaseModelMixin):
    """
    Blood Request Fulfillment Audit Table. (For Member 5)
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
