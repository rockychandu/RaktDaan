"""
Aggregate Inventory Calculation & Matrix Service Layer (Member 4).
Calculates and synchronizes available, reserved, and expired blood bag totals across all 8 blood groups.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import func

from app.database.connection import db
from app.database.models.blood_bank import BloodInventory, BloodBag
from app.common.constants import BloodBagStatus
from app.users.models import BloodGroup

logger = logging.getLogger(__name__)


class InventoryService:
    """
    Business Logic Layer for Aggregate Blood Stock & Inventory Breakdown.
    """

    @staticmethod
    def recalculate_aggregate_inventory_for_blood_group(blood_group: str) -> BloodInventory:
        """
        Recalculates aggregate available, reserved, and expired bag counts for a blood group.
        """
        available_count = BloodBag.query.filter_by(
            blood_group=blood_group,
            status=BloodBagStatus.AVAILABLE.value,
            is_deleted=False
        ).count()

        reserved_count = BloodBag.query.filter_by(
            blood_group=blood_group,
            status=BloodBagStatus.RESERVED.value,
            is_deleted=False
        ).count()

        expired_count = BloodBag.query.filter_by(
            blood_group=blood_group,
            status=BloodBagStatus.EXPIRED.value,
            is_deleted=False
        ).count()

        inv = BloodInventory.query.filter_by(blood_group=blood_group).first()
        if not inv:
            inv = BloodInventory(blood_group=blood_group)
            db.session.add(inv)

        inv.units_available = available_count
        inv.units_reserved = reserved_count
        inv.units_expired = expired_count
        inv.last_updated_at = datetime.now(timezone.utc)

        db.session.commit()
        return inv

    @staticmethod
    def sync_all_blood_groups_inventory() -> List[BloodInventory]:
        """
        Synchronizes aggregate inventory for all 8 blood groups.
        """
        results = []
        for bg in BloodGroup.list_values():
            inv = InventoryService.recalculate_aggregate_inventory_for_blood_group(bg)
            results.append(inv)
        return results

    @staticmethod
    def get_inventory_summary() -> Dict[str, Any]:
        """
        Returns full aggregate inventory summary across all blood groups and bag statuses.
        """
        InventoryService.sync_all_blood_groups_inventory()

        inventories = BloodInventory.query.all()
        by_blood_group = {inv.blood_group: inv.to_dict() for inv in inventories}

        total_available = sum(inv.units_available for inv in inventories)
        total_reserved = sum(inv.units_reserved for inv in inventories)
        total_expired = sum(inv.units_expired for inv in inventories)

        # Status breakdown of all blood bags in database
        status_counts = db.session.query(
            BloodBag.status,
            func.count(BloodBag.id)
        ).filter(BloodBag.is_deleted == False).group_by(BloodBag.status).all()

        bag_status_breakdown = {status.value: 0 for status in BloodBagStatus}
        for st, count in status_counts:
            bag_status_breakdown[st] = count

        return {
            "total_bags_in_system": sum(bag_status_breakdown.values()),
            "total_available_units": total_available,
            "total_reserved_units": total_reserved,
            "total_expired_units": total_expired,
            "bag_status_breakdown": bag_status_breakdown,
            "by_blood_group": by_blood_group
        }
