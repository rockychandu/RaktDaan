"""
Blood Component Separation & Fractionation Service Layer (Member 4).
Fractionates whole blood units into Packed Red Blood Cells (PRBC), Fresh Frozen Plasma (FFP),
and Platelet Concentrates. Generates child blood bags with component-specific shelf lives.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Tuple

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.component_separation import ComponentSeparationRecord
from app.common.constants import BloodBagStatus, ComponentType, COMPONENT_SHELF_LIFE_DAYS
from app.common.exceptions import BloodBagNotFoundException
from app.services.blood_bag_service import BloodBagService, generate_unique_bag_code

logger = logging.getLogger(__name__)


def generate_unique_separation_code() -> str:
    """
    Generates unique component separation code in format SEP-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(ComponentSeparationRecord).count() + 1
    return f"SEP-{year}-{count:06d}"


class ComponentSeparationEngine:
    """
    Business Logic Layer for Blood Bag Component Separation.
    """

    @staticmethod
    def separate_whole_blood(
        parent_bag_id: int,
        technician_user_id: int = 1,
        centrifuge_speed_rpm: int = 3500,
        centrifuge_time_minutes: int = 15,
        prbc_volume_ml: int = 280,
        ffp_volume_ml: int = 220,
        platelet_volume_ml: int = 60
    ) -> Tuple[ComponentSeparationRecord, List[BloodBag]]:
        """
        Processes whole blood bag centrifugation and creates child component bags.
        """
        parent_bag = BloodBagService.get_bag_by_id(parent_bag_id)

        sep_code = generate_unique_separation_code()
        today = date.today()

        record = ComponentSeparationRecord(
            separation_code=sep_code,
            parent_bag_id=parent_bag.id,
            centrifuge_speed_rpm=centrifuge_speed_rpm,
            centrifuge_time_minutes=centrifuge_time_minutes,
            separation_temp_celsius=4.0,
            prbc_volume_ml=prbc_volume_ml,
            ffp_volume_ml=ffp_volume_ml,
            platelet_volume_ml=platelet_volume_ml,
            processed_by_technician_id=technician_user_id,
            status="COMPLETED"
        )
        db.session.add(record)

        child_bags = []
        components_to_create = [
            (ComponentType.PACKED_RED_BLOOD_CELLS.value, prbc_volume_ml),
            (ComponentType.FRESH_FROZEN_PLASMA.value, ffp_volume_ml),
            (ComponentType.PLATELET_CONCENTRATE.value, platelet_volume_ml),
        ]

        for comp_type, volume in components_to_create:
            if volume and volume > 0:
                shelf_days = COMPONENT_SHELF_LIFE_DAYS.get(comp_type, 35)
                child_code = generate_unique_bag_code()
                child_bag = BloodBag(
                    bag_code=child_code,
                    donation_id=parent_bag.donation_id,
                    donor_id=parent_bag.donor_id,
                    blood_group=parent_bag.blood_group,
                    component_type=comp_type,
                    volume_ml=volume,
                    collection_date=parent_bag.collection_date,
                    processing_date=today,
                    expiry_date=parent_bag.collection_date + timedelta(days=shelf_days),
                    status=BloodBagStatus.PROCESSING.value,
                    quality_status=parent_bag.quality_status,
                    notes=f"Fractionated from Parent Bag {parent_bag.bag_code} under Separation {sep_code}"
                )
                db.session.add(child_bag)
                child_bags.append(child_bag)

        # Update parent bag status to DISCARDED (processed into components)
        BloodBagService.transition_bag_status(
            bag_id=parent_bag.id,
            target_status=BloodBagStatus.PROCESSING.value,
            reason=f"Fractionated into components under Separation Code {sep_code}",
            changed_by_user_id=technician_user_id
        )

        db.session.commit()
        logger.info(f"Separated Parent Bag '{parent_bag.bag_code}' into {len(child_bags)} component units.")
        return record, child_bags
