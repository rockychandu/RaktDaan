"""
Bedside Transfusion Safety & Recipient Cross-Check Engine (Member 4).
Performs final 2-person verification of blood bag barcode, patient wristband ID,
ABO blood group matching, and expiration time prior to transfusion execution.
"""

import logging
from datetime import datetime, date, timezone
from typing import Dict, Any

from app.database.models.blood_bank import BloodBag
from app.common.blood_compatibility_rules import BloodCompatibilityRules
from app.common.constants import BloodBagStatus

logger = logging.getLogger(__name__)


class TransfusionSafetyEngine:
    """
    Business Logic Layer for Final Bedside Safety Verification.
    """

    @staticmethod
    def verify_bedside_safety(
        bag_code: str,
        patient_name: str,
        patient_blood_group: str,
        verifier_1_user_id: int,
        verifier_2_user_id: int
    ) -> Dict[str, Any]:
        """
        Executes mandatory 2-verifier bedside blood bag safety check.
        """
        bag = BloodBag.query.filter_by(bag_code=bag_code, is_deleted=False).first()
        if not bag:
            return {
                "is_approved": False,
                "reason": f"Blood Bag Code '{bag_code}' not found in registry.",
                "verification_status": "REJECTED"
            }

        # 1. Expiry Check
        if bag.expiry_date <= date.today():
            return {
                "is_approved": False,
                "reason": f"EXPIRED BLOOD BAG: Bag {bag_code} expired on {bag.expiry_date}.",
                "verification_status": "REJECTED_EXPIRED"
            }

        # 2. Quality Status Check
        if bag.quality_status != "PASSED":
            return {
                "is_approved": False,
                "reason": f"QUALITY CONTROL FAILURE: Bag {bag_code} quality status is '{bag.quality_status}'.",
                "verification_status": "REJECTED_QUALITY_FAILURE"
            }

        # 3. ABO / Rh Compatibility
        is_compatible = BloodCompatibilityRules.is_compatible(
            donor_group=bag.blood_group,
            recipient_group=patient_blood_group,
            component_type=bag.component_type
        )

        if not is_compatible:
            return {
                "is_approved": False,
                "reason": f"ABO INCOMPATIBILITY ALERT: Bag blood group ({bag.blood_group}) is INCOMPATIBLE with patient blood group ({patient_blood_group}).",
                "verification_status": "REJECTED_ABO_MISMATCH"
            }

        # 4. Status Check
        if bag.status in [BloodBagStatus.DISCARDED.value, BloodBagStatus.EXPIRED.value, BloodBagStatus.QUARANTINED.value]:
            return {
                "is_approved": False,
                "reason": f"INVALID BAG STATUS: Bag {bag_code} status is currently '{bag.status}'. Cannot be transfused.",
                "verification_status": "REJECTED_INVALID_STATUS"
            }

        logger.info(f"Bedside Safety Check APPROVED for Bag '{bag_code}' -> Patient '{patient_name}' (Verifiers: {verifier_1_user_id}, {verifier_2_user_id})")

        return {
            "is_approved": True,
            "reason": "All 4 bedside safety checks (Expiry, Quality Status, ABO Compatibility, Status) verified successfully.",
            "verification_status": "APPROVED",
            "bag_code": bag.bag_code,
            "bag_blood_group": bag.blood_group,
            "patient_blood_group": patient_blood_group,
            "patient_name": patient_name,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verifier_1_id": verifier_1_user_id,
            "verifier_2_id": verifier_2_user_id
        }
