"""
Hospital Emergency Request Priority Queue & SLA Dispatch Service Layer (Member 4).
Manages incoming hospital orders, prioritizes emergency STAT requests (<30 min SLA),
allocates compatible blood units, and generates dispatch documentation.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.common.blood_compatibility_rules import BloodCompatibilityRules
from app.common.constants import BloodBagStatus

logger = logging.getLogger(__name__)


class OrderPriority:
    EMERGENCY_STAT = "EMERGENCY_STAT" # SLA < 30 Mins
    URGENT = "URGENT"                 # SLA < 2 Hours
    ROUTINE = "ROUTINE"               # SLA < 24 Hours


class HospitalOrderFulfillmentService:
    """
    Business Logic Layer for Hospital Order Allocation & Priority Queue Management.
    """

    @staticmethod
    def evaluate_emergency_allocation(
        hospital_name: str,
        patient_name: str,
        requested_blood_group: str,
        requested_units: int = 1,
        component_type: str = "PRBC",
        priority: str = OrderPriority.EMERGENCY_STAT
    ) -> Dict[str, Any]:
        """
        Evaluates immediate inventory allocation for emergency hospital request.
        Uses universal donor fallback (O-) if exact group unavailable during EMERGENCY_STAT.
        """
        requested_blood_group = requested_blood_group.upper().strip()

        # 1. Search Exact Match Available Bags (FEFO - Earliest Expiry First)
        exact_bags = BloodBag.query.filter(
            BloodBag.blood_group == requested_blood_group,
            BloodBag.component_type == component_type,
            BloodBag.status == BloodBagStatus.AVAILABLE.value,
            BloodBag.quality_status == "PASSED",
            BloodBag.is_deleted == False
        ).order_by(BloodBag.expiry_date.asc()).limit(requested_units).all()

        allocated_bags = list(exact_bags)

        # 2. Universal Donor Fallback if Emergency STAT and exact stock insufficient
        is_fallback_used = False
        if len(allocated_bags) < requested_units and priority == OrderPriority.EMERGENCY_STAT:
            needed = requested_units - len(allocated_bags)

            # Get compatible blood groups
            compatible_groups = BloodCompatibilityRules.get_compatible_donor_groups(
                recipient_group=requested_blood_group,
                component_type=component_type
            )

            fallback_bags = BloodBag.query.filter(
                BloodBag.blood_group.in_(compatible_groups),
                BloodBag.component_type == component_type,
                BloodBag.status == BloodBagStatus.AVAILABLE.value,
                BloodBag.quality_status == "PASSED",
                BloodBag.id.notin_([b.id for b in allocated_bags]),
                BloodBag.is_deleted == False
            ).order_by(BloodBag.expiry_date.asc()).limit(needed).all()

            allocated_bags.extend(fallback_bags)
            is_fallback_used = True

        is_fulfilled = len(allocated_bags) >= requested_units

        return {
            "hospital_name": hospital_name,
            "patient_name": patient_name,
            "requested_blood_group": requested_blood_group,
            "component_type": component_type,
            "requested_units": requested_units,
            "allocated_units_count": len(allocated_bags),
            "is_fully_fulfilled": is_fulfilled,
            "is_universal_fallback_used": is_fallback_used,
            "priority": priority,
            "allocated_bag_codes": [b.bag_code for b in allocated_bags],
            "allocated_at": datetime.now(timezone.utc).isoformat()
        }
