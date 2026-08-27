"""
Hospital Emergency Transfusion & STAT Order Fulfillment Service.
Allocates emergency blood units, handles universal O- negative fallback matching,
and logs hospital fulfillment SLA metrics.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodRequest, RequestFulfillment
from app.common.constants import BloodBagStatus

logger = logging.getLogger(__name__)


class HospitalTransfusionService:
    """
    Emergency STAT Fulfillment & Universal O- Fallback Engine.
    """

    @staticmethod
    def fulfill_emergency_stat_request(
        hospital_name: str,
        patient_name: str,
        required_blood_group: str,
        units_needed: int,
        is_stat_emergency: bool = True
    ) -> Dict[str, Any]:
        """
        Attempts direct blood group match first; falls back to O- Negative if unavailable!
        """
        # Try direct match
        bags = BloodBag.query.filter_by(
            blood_group=required_blood_group,
            status=BloodBagStatus.AVAILABLE.value,
            is_deleted=False
        ).order_by(BloodBag.expiry_date.asc()).all()

        used_fallback = False
        if len(bags) < units_needed:
            # Fallback to O-
            o_neg_bags = BloodBag.query.filter_by(
                blood_group="O-",
                status=BloodBagStatus.AVAILABLE.value,
                is_deleted=False
            ).order_by(BloodBag.expiry_date.asc()).all()

            if len(o_neg_bags) >= units_needed:
                bags = o_neg_bags
                used_fallback = True
            else:
                return {
                    "fulfilled": False,
                    "message": f"Critical Stock Deficit: Unable to fulfill STAT request for {units_needed} units of {required_blood_group} (O- fallback also insufficient).",
                    "allocated_bags": []
                }

        allocated = bags[:units_needed]
        bag_codes = []

        for b in allocated:
            b.status = BloodBagStatus.DISPATCHED.value
            bag_codes.append(b.bag_code)

        db.session.commit()
        logger.info(f"Fulfilled STAT Request for {hospital_name} ({units_needed} units of {required_blood_group}, Fallback O-: {used_fallback})")

        return {
            "fulfilled": True,
            "hospital_name": hospital_name,
            "patient_name": patient_name,
            "required_blood_group": required_blood_group,
            "used_o_neg_fallback": used_fallback,
            "units_fulfilled": len(allocated),
            "allocated_bag_codes": bag_codes,
            "message": "Emergency STAT order fulfilled successfully."
        }
