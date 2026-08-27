"""
Cold Chain Temperature Excursion Monitoring Models (Member 4).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class TemperatureSensorLog(db.Model, BaseModelMixin):
    """
    Automated Cold Storage Temperature Sensor Reading Log.
    """
    __tablename__ = "temperature_sensor_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    storage_unit_id = db.Column(db.Integer, db.ForeignKey("storage_units.id", ondelete="CASCADE"), nullable=False, index=True)
    reading_temp_celsius = db.Column(db.Float, nullable=False)
    is_excursion = db.Column(db.Boolean, default=False, nullable=False, index=True)
    recorded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "storage_unit_id": self.storage_unit_id,
            "reading_temp_celsius": self.reading_temp_celsius,
            "is_excursion": self.is_excursion,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "notes": self.notes
        }
