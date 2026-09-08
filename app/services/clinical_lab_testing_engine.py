"""
Clinical Laboratory Testing & Pathogen Verification Engine.
Handles automated serology verification (HIV-1/2, HBsAg, HCV Ab, Syphilis, Malaria),
Nucleic Acid Testing (NAT), ABO Subgroup & RhD Typing, Antibody Screening, and Cross-Matching.
"""

import logging
from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.serology import SerologyTestRecord
from app.database.models.inventory_extended import QuarantineRecord
from app.common.constants import BloodBagStatus

logger = logging.getLogger(__name__)


class ClinicalLabTestingEngine:
    """
    Automated Pathogen Screening, Serology, and Subgroup Cross-Matching Engine.
    """

    @staticmethod
    def process_complete_serology_panel(
        bag_id: int,
        hiv_result: str,
        hbv_result: str,
        hcv_result: str,
        syphilis_result: str,
        malaria_result: str,
        nat_hiv_rna: str = "NEGATIVE",
        nat_hbv_dna: str = "NEGATIVE",
        nat_hcv_rna: str = "NEGATIVE",
        abo_subgroup: str = "A1",
        rhd_phenotype: str = "POSITIVE",
        irregular_antibody_screen: str = "NEGATIVE",
        technician_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processes a full pathogen serology and NAT screening panel for a blood bag.
        If any test is POSITIVE or REACTIVE, automatically quarantines the bag!
        """
        bag = BloodBag.query.get(bag_id)
        if not bag:
            raise ValueError(f"Blood Bag ID {bag_id} not found.")

        # Evaluate Serology Panel Results
        results = [
            hiv_result.upper(), hbv_result.upper(), hcv_result.upper(),
            syphilis_result.upper(), malaria_result.upper(),
            nat_hiv_rna.upper(), nat_hbv_dna.upper(), nat_hcv_rna.upper()
        ]

        is_reactive = any(r in ["POSITIVE", "REACTIVE", "DETECTED"] for r in results)

        record = SerologyTestRecord(
            blood_bag_id=bag.id,
            hiv_1_2_ag_ab=hiv_result.upper(),
            hbsag=hbv_result.upper(),
            hcv_ab=hcv_result.upper(),
            syphilis_tppa=syphilis_result.upper(),
            malaria_pf_pv=malaria_result.upper(),
            nat_hiv_rna=nat_hiv_rna.upper(),
            nat_hbv_dna=nat_hbv_dna.upper(),
            nat_hcv_rna=nat_hcv_rna.upper(),
            abo_subgroup=abo_subgroup,
            rhd_phenotype=rhd_phenotype,
            irregular_antibody_screen=irregular_antibody_screen.upper(),
            overall_result="REACTIVE" if is_reactive else "NON_REACTIVE",
            tested_by_user_id=technician_user_id,
            testing_timestamp=datetime.now(timezone.utc)
        )
        db.session.add(record)

        if is_reactive:
            bag.status = BloodBagStatus.QUARANTINED.value
            bag.quality_status = "FAILED_SEROLOGY"
            quarantine = QuarantineRecord(
                blood_bag_id=bag.id,
                quarantine_code=f"QR-SER-{bag.id}",
                reason=f"Pathogen Screening Reactive (HIV:{hiv_result}, HBV:{hbv_result}, HCV:{hcv_result})",
                quarantine_date=datetime.now(timezone.utc),
                status="ACTIVE"
            )
            db.session.add(quarantine)
            logger.warning(f"Blood Bag {bag.bag_code} QUARANTINED due to reactive serology panel!")
        else:
            bag.quality_status = "PASSED"
            logger.info(f"Blood Bag {bag.bag_code} PASSED serology panel.")

        db.session.commit()

        return {
            "bag_id": bag.id,
            "bag_code": bag.bag_code,
            "overall_result": "REACTIVE" if is_reactive else "NON_REACTIVE",
            "quality_status": bag.quality_status,
            "serology_record_id": record.id
        }

    @staticmethod
    def simulate_cross_matching(
        donor_blood_group: str,
        recipient_blood_group: str,
        major_crossmatch: str = "COMPATIBLE",
        minor_crossmatch: str = "COMPATIBLE"
    ) -> Dict[str, Any]:
        """
        Simulates major and minor cross-matching for transfusion safety.
        """
        is_compat = (major_crossmatch.upper() == "COMPATIBLE") and (minor_crossmatch.upper() == "COMPATIBLE")
        return {
            "donor_group": donor_blood_group,
            "recipient_group": recipient_blood_group,
            "major_crossmatch": major_crossmatch.upper(),
            "minor_crossmatch": minor_crossmatch.upper(),
            "is_transfusion_safe": is_compat,
            "recommendation": "APPROVED FOR TRANSFUSION" if is_compat else "INCOMPATIBLE - DO NOT TRANSFUSE"
        }
