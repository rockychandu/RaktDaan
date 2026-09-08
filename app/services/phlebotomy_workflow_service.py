"""
Phlebotomy & Donation Procedure Workflow Service Layer (Member 3).
Handles the 10-step phlebotomy blood collection workflow, including vein assessment,
needle insertion verification, anticoagulant mixing timing, volume monitoring,
and post-donation recovery observation.
"""

import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.donation import DonationRecord
from app.common.constants import DonationStatus
from app.common.exceptions import DonationNotFoundException, InvalidDonationWorkflowState

logger = logging.getLogger(__name__)


class PhlebotomyStep:
    DONOR_IDENTIFICATION = "1_DONOR_IDENTIFICATION"
    VEIN_ASSESSMENT = "2_VEIN_ASSESSMENT"
    SKIN_DISINFECTION = "3_SKIN_DISINFECTION"
    VENIPUNCTURE = "4_VENIPUNCTURE"
    SAMPLE_COLLECTION = "5_SAMPLE_COLLECTION"
    MAIN_BAG_FILLING = "6_MAIN_BAG_FILLING"
    MIXING_ANTICOAGULANT = "7_MIXING_ANTICOAGULANT"
    NEEDLE_WITHDRAWAL = "8_NEEDLE_WITHDRAWAL"
    HEMOSTASIS_BANDAGING = "9_HEMOSTASIS_BANDAGING"
    RECOVERY_OBSERVATION = "10_RECOVERY_OBSERVATION"


class PhlebotomyWorkflowService:
    """
    Business Logic Layer for Standardized Phlebotomy Procedure Execution.
    """

    @staticmethod
    def start_phlebotomy_procedure(
        donation_id: int,
        phlebotomist_user_id: int,
        vein_score: str = "EXCELLENT", # EXCELLENT, GOOD, FAIR, POOR
        needle_gauge: int = 16, # Standard 16G blood collection needle
        anticoagulant_type: str = "CPDA-1" # Citrate Phosphate Dextrose Adenine
    ) -> Dict[str, Any]:
        """
        Initiates phlebotomy collection procedure for an eligible donor donation record.
        """
        donation = DonationRecord.query.filter_by(id=donation_id, is_deleted=False).first()
        if not donation:
            raise DonationNotFoundException(donation_id)

        if donation.donation_status != DonationStatus.ELIGIBLE.value:
            raise InvalidDonationWorkflowState(
                current_state=donation.donation_status,
                target_state=DonationStatus.IN_PROGRESS.value,
                reason="Donation must be in ELIGIBLE status prior to commencing phlebotomy."
            )

        start_time = datetime.now(timezone.utc)
        donation.donation_status = DonationStatus.IN_PROGRESS.value
        db.session.commit()

        logger.info(f"Started Phlebotomy for Donation '{donation.donation_code}' (Phlebotomist ID: {phlebotomist_user_id}, Vein Score: {vein_score})")

        return {
            "donation_id": donation.id,
            "donation_code": donation.donation_code,
            "donor_id": donation.donor_id,
            "phlebotomist_user_id": phlebotomist_user_id,
            "current_step": PhlebotomyStep.VENIPUNCTURE,
            "vein_score": vein_score,
            "needle_gauge": needle_gauge,
            "anticoagulant_type": anticoagulant_type,
            "started_at": start_time.isoformat()
        }

    @staticmethod
    def monitor_collection_progress(
        donation_id: int,
        elapsed_minutes: float,
        current_volume_ml: int
    ) -> Dict[str, Any]:
        """
        Monitors blood bag collection volume and flow rate.
        Flag draw times > 15 minutes as slow draws (risk of micro-clotting).
        """
        donation = DonationRecord.query.filter_by(id=donation_id, is_deleted=False).first()
        if not donation:
            raise DonationNotFoundException(donation_id)

        is_slow_draw = elapsed_minutes > 15.0
        is_target_reached = current_volume_ml >= 450

        status_summary = "IN_PROGRESS"
        if is_target_reached:
            status_summary = "TARGET_VOLUME_REACHED"
        elif is_slow_draw:
            status_summary = "SLOW_DRAW_WARNING"

        return {
            "donation_id": donation.id,
            "current_volume_ml": current_volume_ml,
            "target_volume_ml": 450,
            "elapsed_minutes": elapsed_minutes,
            "is_slow_draw": is_slow_draw,
            "is_target_reached": is_target_reached,
            "status_summary": status_summary
        }
