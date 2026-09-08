"""
Internal Notification & Alert Center Service Layer (Member 4).
DB-backed notification management system for low stock, expiring bags, quarantine alerts, and system events.
No third-party APIs or external services required.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.notification import InternalNotification
from app.common.constants import NotificationPriority, NotificationCategory

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Business Logic Layer for Internal System Notifications & Alert Center.
    """

    @staticmethod
    def create_notification(
        title: str,
        message: str,
        category: str = NotificationCategory.IMPORTANT_EVENT.value,
        priority: str = NotificationPriority.MEDIUM.value,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None
    ) -> InternalNotification:
        """
        Creates and persists a new internal alert notification.
        """
        notif = InternalNotification(
            title=title,
            message=message,
            category=category,
            priority=priority,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            is_read=False,
            is_acknowledged=False
        )
        db.session.add(notif)
        db.session.commit()
        logger.info(f"Created Notification [{priority}]: '{title}'")
        return notif

    @staticmethod
    def mark_as_read(notification_id: int) -> InternalNotification:
        """
        Marks a notification as read.
        """
        notif = InternalNotification.query.filter_by(id=notification_id, is_deleted=False).first()
        if notif:
            notif.is_read = True
            notif.read_at = datetime.now(timezone.utc)
            db.session.commit()
        return notif

    @staticmethod
    def acknowledge_notification(notification_id: int, user_id: int) -> InternalNotification:
        """
        Acknowledges an alert by an authorized admin user.
        """
        notif = InternalNotification.query.filter_by(id=notification_id, is_deleted=False).first()
        if notif:
            notif.is_read = True
            notif.is_acknowledged = True
            notif.acknowledged_by_user_id = user_id
            notif.acknowledged_at = datetime.now(timezone.utc)
            db.session.commit()
        return notif

    @staticmethod
    def get_unread_notifications(limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves unread notifications ordered by priority and date.
        """
        notifs = InternalNotification.query.filter_by(is_read=False, is_deleted=False)\
            .order_by(InternalNotification.created_at.desc()).limit(limit).all()
        return [n.to_dict() for n in notifs]

    @staticmethod
    def get_all_notifications(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Lists and paginates all internal notifications.
        """
        query = InternalNotification.query.filter_by(is_deleted=False).order_by(InternalNotification.created_at.desc())
        total = query.count()
        unread_count = InternalNotification.query.filter_by(is_read=False, is_deleted=False).count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": [n.to_dict() for n in items],
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
