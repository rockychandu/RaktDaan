"""
Blood Bank Logistics, Transport Containers & Vehicle Surveillance Models (Member 4).
Tracks insulated transport boxes, temperature data loggers, delivery vehicles, and transport legs.
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class TransportContainer(db.Model, BaseModelMixin):
    """
    Insulated Blood Transport Box / Carrier Equipment.
    """
    __tablename__ = "transport_containers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    container_type = db.Column(db.String(50), nullable=False, default="INSULATED_COOL_BOX") # COOL_BOX, THERMAL_VALIDATED, DRY_ICE_CHEST
    capacity_bags = db.Column(db.Integer, nullable=False, default=10)
    coolant_type = db.Column(db.String(50), nullable=False, default="WET_ICE_PACKS") # WET_ICE_PACKS, PHASE_CHANGE_MATERIAL, DRY_ICE
    max_hold_time_hours = db.Column(db.Float, nullable=False, default=6.0)
    status = db.Column(db.String(30), nullable=False, default="AVAILABLE") # AVAILABLE, IN_TRANSIT, MAINTENANCE, DECOMMISSIONED"
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "container_code": self.container_code,
            "name": self.name,
            "container_type": self.container_type,
            "capacity_bags": self.capacity_bags,
            "coolant_type": self.coolant_type,
            "max_hold_time_hours": self.max_hold_time_hours,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TransportLeg(db.Model, BaseModelMixin):
    """
    Blood Bag Transport Leg / Dispatch Shipment Log.
    """
    __tablename__ = "transport_legs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shipment_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    container_id = db.Column(db.Integer, db.ForeignKey("transport_containers.id"), nullable=False)
    dispatch_id = db.Column(db.Integer, db.ForeignKey("blood_dispatches.id"), nullable=True)
    origin_location = db.Column(db.String(150), nullable=False)
    destination_hospital = db.Column(db.String(150), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone = db.Column(db.String(20), nullable=False)
    departure_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    estimated_arrival_time = db.Column(db.DateTime(timezone=True), nullable=True)
    actual_arrival_time = db.Column(db.DateTime(timezone=True), nullable=True)
    departure_temp_celsius = db.Column(db.Float, nullable=False, default=4.0)
    arrival_temp_celsius = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="IN_TRANSIT") # IN_TRANSIT, DELIVERED, DELAYED, BREACHED
    seal_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "shipment_code": self.shipment_code,
            "container_id": self.container_id,
            "dispatch_id": self.dispatch_id,
            "origin_location": self.origin_location,
            "destination_hospital": self.destination_hospital,
            "driver_name": self.driver_name,
            "driver_phone": self.driver_phone,
            "departure_time": self.departure_time.isoformat() if self.departure_time else None,
            "estimated_arrival_time": self.estimated_arrival_time.isoformat() if self.estimated_arrival_time else None,
            "actual_arrival_time": self.actual_arrival_time.isoformat() if self.actual_arrival_time else None,
            "departure_temp_celsius": self.departure_temp_celsius,
            "arrival_temp_celsius": self.arrival_temp_celsius,
            "status": self.status,
            "seal_number": self.seal_number,
            "notes": self.notes
        }
