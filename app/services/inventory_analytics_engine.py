"""
Inventory Analytics & Efficiency Metrics Engine (Member 4).
Calculates wastage rate, utilization rate, stock turnover ratio, collection trends, and storage duration.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy import func

from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.donation import DonationRecord
from app.database.models.inventory_extended import BloodDispatch
from app.common.constants import BloodBagStatus

logger = logging.getLogger(__name__)


class InventoryAnalyticsEngine:
    """
    Analytics & Performance Metric Engine for Blood Inventory.
    """

    @staticmethod
    def get_inventory_analytics_overview() -> Dict[str, Any]:
        """
        Calculates key inventory operational metrics and analytics.
        """
        total_collected = BloodBag.query.filter_by(is_deleted=False).count()

        total_dispatched = db.session.query(func.sum(BloodDispatch.quantity_units)).scalar() or 0
        total_dispatched = int(total_dispatched)

        total_expired = BloodBag.query.filter_by(
            status=BloodBagStatus.EXPIRED.value,
            is_deleted=False
        ).count()

        total_discarded = BloodBag.query.filter_by(
            status=BloodBagStatus.DISCARDED.value,
            is_deleted=False
        ).count()

        total_wastage = total_expired + total_discarded

        # Wastage Percentage
        wastage_percentage = round((total_wastage / total_collected * 100), 2) if total_collected > 0 else 0.0

        # Utilization Rate (Dispatched / Total Collected)
        utilization_rate_percent = round((total_dispatched / total_collected * 100), 2) if total_collected > 0 else 0.0

        # Average Storage Duration (Collection date to Dispatch date)
        dispatched_bags = BloodBag.query.filter_by(
            status=BloodBagStatus.DISPATCHED.value,
            is_deleted=False
        ).all()

        total_days = 0
        valid_bags_count = 0
        for bag in dispatched_bags:
            if bag.collection_date and bag.updated_at:
                days = (bag.updated_at.date() - bag.collection_date).days
                if days >= 0:
                    total_days += days
                    valid_bags_count += 1

        avg_storage_days = round(total_days / valid_bags_count, 1) if valid_bags_count > 0 else 0.0

        return {
            "total_bags_collected": total_collected,
            "total_bags_dispatched": total_dispatched,
            "total_bags_expired": total_expired,
            "total_bags_discarded": total_discarded,
            "total_wastage_units": total_wastage,
            "wastage_percentage": wastage_percentage,
            "utilization_rate_percent": utilization_rate_percent,
            "avg_storage_duration_days": avg_storage_days
        }
