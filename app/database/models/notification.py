"""
Internal Notification & Alert Center Database Model (Member 4).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin
from app.common.constants import NotificationPriority, NotificationCategory


class InternalNotification(db.Model, BaseModelMixin):
    """
    Internal Database-backed Notification Center Table for System Alerts.
    """
    __tablename__ = "internal_notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default=NotificationCategory.IMPORTANT_EVENT.value, index=True)
    priority = db.Column(db.String(20), nullable=False, default=NotificationPriority.MEDIUM.value, index=True)
    related_entity_type = db.Column(db.String(50), nullable=True) # BloodBag, StorageUnit, Reservation, StockThreshold
    related_entity_id = db.Column(db.String(50), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_acknowledged = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
    acknowledged_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    acknowledged_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "category": self.category,
            "priority": self.priority,
            "related_entity_type": self.related_entity_type,
            "related_entity_id": self.related_entity_id,
            "is_read": self.is_read,
            "is_acknowledged": self.is_acknowledged,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "acknowledged_by_user_id": self.acknowledged_by_user_id,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<InternalNotification id={self.id} category='{self.category}' priority='{self.priority}'>"
