"""
Inventory FEFO (First-Expired, First-Out) Allocation Engine & Quarantine Recovery Service.
Optimizes blood bag allocation based on earliest expiry date, compatibility, and component type.
"""

import logging
from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.inventory_extended import QuarantineRecord, BloodReservation
from app.common.constants import BloodBagStatus, ComponentType

logger = logging.getLogger(__name__)


class InventoryFEFOAllocationEngine:
    """
    Business Service for FEFO Blood Unit Allocation and Storage Reconciliation.
    """

    @staticmethod
    def allocate_fefo_bags(
        required_blood_group: str,
        required_units: int,
        component_type: str = ComponentType.WHOLE_BLOOD.value,
        hospital_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Selects available blood bags strictly sorted by earliest expiry date (FEFO).
        """
        available_bags = BloodBag.query.filter_by(
            blood_group=required_blood_group,
            component_type=component_type,
            status=BloodBagStatus.AVAILABLE.value,
            is_deleted=False
        ).order_by(BloodBag.expiry_date.asc()).all()

        if len(available_bags) < required_units:
            return {
                "allocated": False,
                "available_units": len(available_bags),
                "required_units": required_units,
                "message": f"Insufficient stock of {required_blood_group} ({len(available_bags)} available, {required_units} requested).",
                "allocated_bags": []
            }

        selected = available_bags[:required_units]
        allocated_data = []

        for bag in selected:
            bag.status = BloodBagStatus.RESERVED.value
            res = BloodReservation(
                blood_bag_id=bag.id,
                hospital_name=hospital_id or "General Hospital",
                reservation_code=f"RES-{bag.id:05d}",
                reserved_at=datetime.now(timezone.utc),
                status="ACTIVE"
            )
            db.session.add(res)
            allocated_data.append({
                "bag_id": bag.id,
                "bag_code": bag.bag_code,
                "expiry_date": bag.expiry_date.isoformat() if bag.expiry_date else None,
                "volume_ml": bag.volume_ml
            })

        db.session.commit()
        logger.info(f"Allocated {required_units} FEFO units for group {required_blood_group}")

        return {
            "allocated": True,
            "required_units": required_units,
            "allocated_units_count": len(selected),
            "allocated_bags": allocated_data,
            "message": f"Successfully reserved {required_units} FEFO units of {required_blood_group}."
        }

    @staticmethod
    def release_quarantine_unit(quarantine_id: int, reviewer_user_id: int, release_reason: str) -> Dict[str, Any]:
        """
        Releases a unit from quarantine back to AVAILABLE status after secondary inspection.
        """
        q = QuarantineRecord.query.get(quarantine_id)
        if not q:
            raise ValueError(f"Quarantine Record ID {quarantine_id} not found.")

        q.status = "RELEASED"
        q.resolution_notes = release_reason

        bag = q.blood_bag
        if bag:
            bag.status = BloodBagStatus.AVAILABLE.value
            bag.quality_status = "PASSED"

        db.session.commit()
        logger.info(f"Released Quarantine ID {quarantine_id} for Bag {bag.bag_code if bag else ''}")

        return {
            "quarantine_id": q.id,
            "bag_code": bag.bag_code if bag else None,
            "status": "RELEASED",
            "message": "Quarantine unit released back to available inventory."
        }
