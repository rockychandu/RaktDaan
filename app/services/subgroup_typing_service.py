"""
Subgroup Typing & Extended Rh Phenotype Service Layer (Member 3 & Member 4).
Handles A1 vs A2 subgroup determination, extended Rh phenotype antigen typing (Big C, Little c, Big E, Little e),
and Kell (K1/K2) antigen compatibility screening.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.models.blood_bank import BloodBag

logger = logging.getLogger(__name__)


class SubgroupTypingService:
    """
    Business Logic Layer for Advanced Immunohaematology & Subgroup Phenotyping.
    """

    @staticmethod
    def evaluate_subgroup_typing(
        bag_id: int,
        anti_a1_lectin_result: str = "POSITIVE", # POSITIVE = A1, NEGATIVE = A2
        rh_c_antigen: bool = True,   # C
        rh_c_little_antigen: bool = True, # c
        rh_e_antigen: bool = False,  # E
        rh_e_little_antigen: bool = True, # e
        kell_antigen_k: bool = False # K1 Kell Antigen
    ) -> Dict[str, Any]:
        """
        Processes extended immunohaematology subgroup results.
        """
        bag = BloodBag.query.get(bag_id)
        bag_code = bag.bag_code if bag else f"BAG-{bag_id}"

        # Subgroup classification
        subgroup = "A1" if anti_a1_lectin_result.upper() == "POSITIVE" else "A2"

        # Rh Phenotype string construction (e.g. C+ c+ E- e+)
        rh_phenotype = f"C{'+' if rh_c_antigen else '-'} c{'+' if rh_c_little_antigen else '-'} E{'+' if rh_e_antigen else '-'} e{'+' if rh_e_little_antigen else '-'}"
        kell_status = "K+" if kell_antigen_k else "K-"

        logger.info(f"Evaluated Subgroup Typing for Bag '{bag_code}': Subgroup={subgroup}, Rh Phenotype={rh_phenotype}, Kell={kell_status}")

        return {
            "bag_id": bag_id,
            "bag_code": bag_code,
            "subgroup": subgroup,
            "anti_a1_lectin_result": anti_a1_lectin_result,
            "rh_phenotype": rh_phenotype,
            "kell_status": kell_status,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
