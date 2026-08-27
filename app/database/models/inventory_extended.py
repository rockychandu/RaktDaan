"""
Extended Blood Inventory, Storage Hierarchy, Reservations, Dispatches, Quarantine, & Reconciliation Models (Member 4).
"""

from datetime import datetime, timezone, timedelta
from app.database.connection import db
from app.database.base import BaseModelMixin
from app.common.constants import BloodBagStatus, ComponentType, StorageType, StockLevelStatus, TransactionType


class StorageUnit(db.Model, BaseModelMixin):
    """
    Physical Cold Storage Equipment Entity (Refrigerators, Deep Freezers, Agitators).
    """
    __tablename__ = "storage_units"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    unit_type = db.Column(db.String(50), nullable=False, default=StorageType.BLOOD_REFRIGERATOR.value)
    section_location = db.Column(db.String(100), nullable=False)
    total_capacity_units = db.Column(db.Integer, nullable=False, default=200)
    occupied_units = db.Column(db.Integer, nullable=False, default=0)
    min_temp_celsius = db.Column(db.Float, nullable=False, default=2.0)
    max_temp_celsius = db.Column(db.Float, nullable=False, default=6.0)
    status = db.Column(db.String(20), nullable=False, default="ACTIVE") # ACTIVE, MAINTENANCE, INACTIVE
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    locations = db.relationship("StorageLocation", backref="storage_unit", cascade="all, delete-orphan")
    blood_bags = db.relationship("BloodBag", backref="storage_unit")

    @property
    def available_capacity(self) -> int:
        return max(0, self.total_capacity_units - self.occupied_units)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit_type": self.unit_type,
            "section_location": self.section_location,
            "total_capacity_units": self.total_capacity_units,
            "occupied_units": self.occupied_units,
            "available_capacity": self.available_capacity,
            "min_temp_celsius": self.min_temp_celsius,
            "max_temp_celsius": self.max_temp_celsius,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class StorageLocation(db.Model, BaseModelMixin):
    """
    Detailed Hierarchy Position (Unit -> Rack -> Shelf -> Position).
    """
    __tablename__ = "storage_locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    storage_unit_id = db.Column(db.Integer, db.ForeignKey("storage_units.id", ondelete="CASCADE"), nullable=False, index=True)
    rack_number = db.Column(db.String(50), nullable=False, default="Rack-1")
    shelf_number = db.Column(db.String(50), nullable=False, default="Shelf-1")
    position_number = db.Column(db.String(50), nullable=False, default="Pos-1")
    is_occupied = db.Column(db.Boolean, default=False, nullable=False)
    assigned_bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="SET NULL"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "storage_unit_id": self.storage_unit_id,
            "unit_name": self.storage_unit.name if self.storage_unit else None,
            "rack_number": self.rack_number,
            "shelf_number": self.shelf_number,
            "position_number": self.position_number,
            "is_occupied": self.is_occupied,
            "assigned_bag_id": self.assigned_bag_id
        }


class BloodBagStatusLog(db.Model, BaseModelMixin):
    """
    Immutable State Transition Audit Trail for Blood Bags.
    """
    __tablename__ = "blood_bag_status_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status = db.Column(db.String(30), nullable=False)
    new_status = db.Column(db.String(30), nullable=False)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reason = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "bag_id": self.bag_id,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "changed_by_user_id": self.changed_by_user_id,
            "reason": self.reason,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class InventoryTransaction(db.Model, BaseModelMixin):
    """
    Centralized Inventory Delta Audit Ledger Table.
    """
    __tablename__ = "inventory_transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="SET NULL"), nullable=True, index=True)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    component_type = db.Column(db.String(50), nullable=False, default=ComponentType.WHOLE_BLOOD.value)
    quantity_units = db.Column(db.Integer, nullable=False, default=1)
    transaction_type = db.Column(db.String(50), nullable=False, index=True)
    previous_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=True)
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reason = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_code": self.transaction_code,
            "bag_id": self.bag_id,
            "blood_group": self.blood_group,
            "component_type": self.component_type,
            "quantity_units": self.quantity_units,
            "transaction_type": self.transaction_type,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "performed_by_user_id": self.performed_by_user_id,
            "reason": self.reason,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class StockThreshold(db.Model, BaseModelMixin):
    """
    Configurable Low and Critical Stock Threshold Rules per Blood Group.
    """
    __tablename__ = "stock_thresholds"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blood_group = db.Column(db.String(10), unique=True, nullable=False, index=True)
    minimum_units = db.Column(db.Integer, nullable=False, default=10)
    critical_units = db.Column(db.Integer, nullable=False, default=4)
    status = db.Column(db.String(20), nullable=False, default=StockLevelStatus.NORMAL.value)
    last_evaluated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "blood_group": self.blood_group,
            "minimum_units": self.minimum_units,
            "critical_units": self.critical_units,
            "status": self.status,
            "last_evaluated_at": self.last_evaluated_at.isoformat() if self.last_evaluated_at else None
        }


class BloodReservation(db.Model, BaseModelMixin):
    """
    Blood Reservation Entity for Future Requests & Hospitals.
    """
    __tablename__ = "blood_reservations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    reference_request_id = db.Column(db.String(100), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    component_type = db.Column(db.String(50), nullable=False, default=ComponentType.WHOLE_BLOOD.value)
    quantity_units = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default="ACTIVE") # ACTIVE, DISPATCHED, RELEASED, EXPIRED
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Junction table mapping reserved blood bags
    reserved_bags = db.relationship("BloodBag", secondary="reservation_bag_map", backref="reservations")

    def to_dict(self):
        return {
            "id": self.id,
            "reservation_code": self.reservation_code,
            "reference_request_id": self.reference_request_id,
            "hospital_name": self.hospital_name,
            "patient_name": self.patient_name,
            "blood_group": self.blood_group,
            "component_type": self.component_type,
            "quantity_units": self.quantity_units,
            "status": self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_by_user_id": self.created_by_user_id,
            "reserved_bag_codes": [b.bag_code for b in self.reserved_bags],
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# Secondary Map Table for Reservation -> BloodBags
reservation_bag_map = db.Table(
    "reservation_bag_map",
    db.Column("reservation_id", db.Integer, db.ForeignKey("blood_reservations.id", ondelete="CASCADE"), primary_key=True),
    db.Column("bag_id", db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), primary_key=True)
)


class BloodDispatch(db.Model, BaseModelMixin):
    """
    Hospital Dispatch Order Table.
    """
    __tablename__ = "blood_dispatches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dispatch_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey("blood_reservations.id", ondelete="SET NULL"), nullable=True)
    reference_request_id = db.Column(db.String(100), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    recipient_patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    component_type = db.Column(db.String(50), nullable=False)
    quantity_units = db.Column(db.Integer, nullable=False)
    dispatch_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    dispatched_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="COMPLETED") # COMPLETED, IN_TRANSIT, CANCELLED
    transport_box_temp_celsius = db.Column(db.Float, default=4.0, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Dispatched bags mapping
    dispatched_bags = db.relationship("BloodBag", secondary="dispatch_bag_map", backref="dispatches")

    def to_dict(self):
        return {
            "id": self.id,
            "dispatch_code": self.dispatch_code,
            "reservation_id": self.reservation_id,
            "reference_request_id": self.reference_request_id,
            "hospital_name": self.hospital_name,
            "recipient_patient_name": self.recipient_patient_name,
            "blood_group": self.blood_group,
            "component_type": self.component_type,
            "quantity_units": self.quantity_units,
            "dispatch_date": self.dispatch_date.isoformat() if self.dispatch_date else None,
            "dispatched_by_user_id": self.dispatched_by_user_id,
            "status": self.status,
            "transport_box_temp_celsius": self.transport_box_temp_celsius,
            "dispatched_bag_codes": [b.bag_code for b in self.dispatched_bags],
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# Secondary Map Table for Dispatch -> BloodBags
dispatch_bag_map = db.Table(
    "dispatch_bag_map",
    db.Column("dispatch_id", db.Integer, db.ForeignKey("blood_dispatches.id", ondelete="CASCADE"), primary_key=True),
    db.Column("bag_id", db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), primary_key=True)
)


class QuarantineRecord(db.Model, BaseModelMixin):
    """
    Blood Bag Quarantine Management Table.
    """
    __tablename__ = "quarantine_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), nullable=False, index=True)
    quarantine_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    reason = db.Column(db.String(255), nullable=False)
    suspected_issue = db.Column(db.Text, nullable=True)
    quarantined_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quarantine_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="ACTIVE") # ACTIVE, RESOLVED_RELEASED, RESOLVED_DISCARDED
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolved_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "quarantine_code": self.quarantine_code,
            "bag_id": self.bag_id,
            "bag_code": self.blood_bag.bag_code if self.blood_bag else None,
            "reason": self.reason,
            "suspected_issue": self.suspected_issue,
            "quarantined_by_user_id": self.quarantined_by_user_id,
            "quarantine_date": self.quarantine_date.isoformat() if self.quarantine_date else None,
            "status": self.status,
            "resolution_notes": self.resolution_notes,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by_user_id": self.resolved_by_user_id
        }


class BloodReturnRecall(db.Model, BaseModelMixin):
    """
    Hospital Return & Safety Recall Audit Table.
    """
    __tablename__ = "blood_returns_recalls"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    return_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), nullable=False, index=True)
    return_source = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    inspection_notes = db.Column(db.Text, nullable=True)
    disposition = db.Column(db.String(30), nullable=False, default="QUARANTINED") # RETURNED_TO_STOCK, QUARANTINED, DISCARDED
    processed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    return_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "return_code": self.return_code,
            "bag_id": self.bag_id,
            "return_source": self.return_source,
            "reason": self.reason,
            "inspection_notes": self.inspection_notes,
            "disposition": self.disposition,
            "processed_by_user_id": self.processed_by_user_id,
            "return_date": self.return_date.isoformat() if self.return_date else None
        }


class StockReconciliation(db.Model, BaseModelMixin):
    """
    Physical Stock Audit & System Variance Ledger.
    """
    __tablename__ = "stock_reconciliations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reconciliation_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    component_type = db.Column(db.String(50), nullable=False, default=ComponentType.WHOLE_BLOOD.value)
    system_count = db.Column(db.Integer, nullable=False)
    physical_count = db.Column(db.Integer, nullable=False)
    variance_count = db.Column(db.Integer, nullable=False) # physical - system
    audit_reason = db.Column(db.String(255), nullable=False)
    audited_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    audit_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "reconciliation_code": self.reconciliation_code,
            "blood_group": self.blood_group,
            "component_type": self.component_type,
            "system_count": self.system_count,
            "physical_count": self.physical_count,
            "variance_count": self.variance_count,
            "audit_reason": self.audit_reason,
            "audited_by_user_id": self.audited_by_user_id,
            "audit_date": self.audit_date.isoformat() if self.audit_date else None
        }
