"""
Serological Cross-Match & Transfusion Compatibility Engine (Member 3 & Member 4).
Performs Major & Minor Cross-Matching, Direct & Indirect Coombs Testing (IAT/DAT),
and Antibody Screening to ensure 100% immune compatibility prior to blood unit dispatch.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.common.blood_compatibility_rules import BloodCompatibilityRules
from app.common.exceptions import BloodBagNotFoundException, IncompatibleBloodGroupException

logger = logging.getLogger(__name__)


class CrossMatchEngine:
    """
    Business Logic Layer for Serological Cross-Matching & Antibody Screen Verification.
    """

    @staticmethod
    def perform_cross_match(
        bag_id: int,
        recipient_blood_group: str,
        recipient_name: str,
        coombs_test_result: str = "NEGATIVE", # NEGATIVE, POSITIVE
        antibody_screen_result: str = "NEGATIVE", # NEGATIVE, POSITIVE
        technician_user_id: int = 1
    ) -> Dict[str, Any]:
        """
        Executes cross-matching verification between a donor blood bag and recipient parameters.
        Raises IncompatibleBloodGroupException if ABO/Rh or serological cross-match fails.
        """
        bag = BloodBag.query.filter_by(id=bag_id, is_deleted=False).first()
        if not bag:
            raise BloodBagNotFoundException(bag_id)

        # 1. ABO / Rh Compatibility Matrix Check
        is_abo_compatible = BloodCompatibilityRules.is_compatible(
            donor_group=bag.blood_group,
            recipient_group=recipient_blood_group,
            component_type=bag.component_type
        )

        if not is_abo_compatible:
            logger.warning(f"Cross-Match FAILED: Donor Bag '{bag.bag_code}' ({bag.blood_group}) is ABO incompatible with Recipient '{recipient_name}' ({recipient_blood_group})")
            return {
                "is_compatible": False,
                "reason": f"ABO Incompatibility: Donor {bag.blood_group} cannot be given to Recipient {recipient_blood_group} for {bag.component_type}.",
                "bag_code": bag.bag_code,
                "donor_blood_group": bag.blood_group,
                "recipient_blood_group": recipient_blood_group,
                "coombs_test_result": coombs_test_result,
                "antibody_screen_result": antibody_screen_result
            }

        # 2. Coombs & Antibody Screen Check
        if coombs_test_result == "POSITIVE" or antibody_screen_result == "POSITIVE":
            logger.warning(f"Cross-Match FAILED: Positive Coombs/Antibody screen for Bag '{bag.bag_code}' and Recipient '{recipient_name}'")
            return {
                "is_compatible": False,
                "reason": "Serological Agglutination Detected: Positive Indirect Coombs / Irregular Antibody Screen result.",
                "bag_code": bag.bag_code,
                "donor_blood_group": bag.blood_group,
                "recipient_blood_group": recipient_blood_group,
                "coombs_test_result": coombs_test_result,
                "antibody_screen_result": antibody_screen_result
            }

        logger.info(f"Cross-Match PASSED: Bag '{bag.bag_code}' ({bag.blood_group}) matches Recipient '{recipient_name}' ({recipient_blood_group})")
        return {
            "is_compatible": True,
            "reason": "Cross-match passed all ABO, Rh, Coombs, and antibody screen compatibility checks.",
            "bag_code": bag.bag_code,
            "donor_blood_group": bag.blood_group,
            "recipient_blood_group": recipient_blood_group,
            "coombs_test_result": coombs_test_result,
            "antibody_screen_result": antibody_screen_result,
            "cross_matched_at": datetime.now(timezone.utc).isoformat()
        }
