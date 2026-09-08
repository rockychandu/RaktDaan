"""
Automatic Expiry Protection & Warning Scanner Engine (Member 4).
Scans inventory for expired or expiring-soon blood bags, updates statuses, and triggers internal alerts.
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any, List

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.inventory_extended import BloodBagStatusLog
from app.common.constants import BloodBagStatus, DEFAULT_EXPIRY_WARNING_DAYS, NotificationCategory, NotificationPriority
from app.services.inventory_service import InventoryService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class ExpiryEngine:
    """
    Automated Expiry Detection & Stock Exclusion Engine.
    """

    @staticmethod
    def run_automatic_expiry_check(warning_days: int = DEFAULT_EXPIRY_WARNING_DAYS) -> Dict[str, Any]:
        """
        Executes full expiry scanning cycle.
        Transitions expired bags to EXPIRED status, excludes them from available stock, and fires alerts.
        """
        today = date.today()
        warning_cutoff = today + timedelta(days=warning_days)

        # 1. Identify Expired Bags currently listed as AVAILABLE or RESERVED
        expired_bags = BloodBag.query.filter(
            BloodBag.expiry_date <= today,
            BloodBag.status.in_([BloodBagStatus.AVAILABLE.value, BloodBagStatus.RESERVED.value]),
            BloodBag.is_deleted == False
        ).all()

        transitioned_count = 0
        for bag in expired_bags:
            prev_status = bag.status
            bag.status = BloodBagStatus.EXPIRED.value

            # Log status change
            log = BloodBagStatusLog(
                bag_id=bag.id,
                previous_status=prev_status,
                new_status=BloodBagStatus.EXPIRED.value,
                reason=f"Automatic Expiry Engine: Passed expiry date {bag.expiry_date.isoformat()}."
            )
            db.session.add(log)

            # Trigger Expiry Alert
            NotificationService.create_notification(
                title=f"Expired Blood Bag Alert: {bag.bag_code}",
                message=f"Blood bag {bag.bag_code} ({bag.blood_group} {bag.component_type}) expired on {bag.expiry_date.isoformat()} and has been excluded from available stock.",
                category=NotificationCategory.EXPIRED_STOCK.value,
                priority=NotificationPriority.HIGH.value,
                related_entity_type="BloodBag",
                related_entity_id=str(bag.id)
            )
            transitioned_count += 1

        db.session.commit()

        # 2. Identify Expiring Soon Bags
        expiring_soon_bags = BloodBag.query.filter(
            BloodBag.expiry_date > today,
            BloodBag.expiry_date <= warning_cutoff,
            BloodBag.status == BloodBagStatus.AVAILABLE.value,
            BloodBag.is_deleted == False
        ).all()

        for bag in expiring_soon_bags:
            days_left = (bag.expiry_date - today).days
            NotificationService.create_notification(
                title=f"Expiring Soon: {bag.bag_code} ({days_left} days left)",
                message=f"Blood bag {bag.bag_code} ({bag.blood_group} {bag.component_type}) will expire on {bag.expiry_date.isoformat()} ({days_left} days remaining).",
                category=NotificationCategory.EXPIRING_SOON.value,
                priority=NotificationPriority.MEDIUM.value if days_left > 2 else NotificationPriority.HIGH.value,
                related_entity_type="BloodBag",
                related_entity_id=str(bag.id)
            )

        # Recalculate inventory
        InventoryService.sync_all_blood_groups_inventory()

        logger.info(f"Expiry Engine Scan Complete: {transitioned_count} bags marked EXPIRED, {len(expiring_soon_bags)} bags expiring soon.")

        return {
            "expired_bags_count": len(expired_bags),
            "transitioned_to_expired": transitioned_count,
            "expiring_soon_count": len(expiring_soon_bags),
            "warning_days_window": warning_days,
            "scanned_at": today.isoformat()
        }
