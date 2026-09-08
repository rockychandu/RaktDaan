"""
Blood Component Separation & Fractionation Database Models (Member 4).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class ComponentSeparationRecord(db.Model, BaseModelMixin):
    """
    Blood Component Separation & Centrifugation Processing Log.
    Tracks parent whole blood bag fractionation into child component bags.
    """
    __tablename__ = "component_separation_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    separation_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    parent_bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), nullable=False, index=True)
    centrifuge_speed_rpm = db.Column(db.Integer, nullable=False, default=3500)
    centrifuge_time_minutes = db.Column(db.Integer, nullable=False, default=15)
    separation_temp_celsius = db.Column(db.Float, nullable=False, default=4.0)
    prbc_volume_ml = db.Column(db.Integer, nullable=True, default=280)
    ffp_volume_ml = db.Column(db.Integer, nullable=True, default=220)
    platelet_volume_ml = db.Column(db.Integer, nullable=True, default=60)
    processed_by_technician_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="COMPLETED")
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "separation_code": self.separation_code,
            "parent_bag_id": self.parent_bag_id,
            "centrifuge_speed_rpm": self.centrifuge_speed_rpm,
            "centrifuge_time_minutes": self.centrifuge_time_minutes,
            "separation_temp_celsius": self.separation_temp_celsius,
            "prbc_volume_ml": self.prbc_volume_ml,
            "ffp_volume_ml": self.ffp_volume_ml,
            "platelet_volume_ml": self.platelet_volume_ml,
            "processed_by_technician_id": self.processed_by_technician_id,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
