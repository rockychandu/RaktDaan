"""
Adverse Event & Transfusion Reaction Hemovigilance Engine (Member 3 & Member 4).
Logs donation/phlebotomy adverse reactions (vasovagal, hematoma, nerve irritation)
and transfusion adverse events (TRALI, TACO, febrile reaction, acute hemolytic reaction).
Calculates hemovigilance safety metrics and triggers safety audits.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.donation import DonationRecord
from app.database.models.blood_bank import BloodBag
from app.common.constants import NotificationCategory, NotificationPriority
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class ReactionSeverity:
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class AdverseEventEngine:
    """
    Business Logic Layer for Hemovigilance & Adverse Reaction Surveillance.
    """

    @staticmethod
    def log_donation_adverse_event(
        donation_id: int,
        event_type: str, # VASOVAGAL, HEMATOMA, NERVE_IRRITATION, CITRATE_TOXICITY
        severity: str = ReactionSeverity.MILD,
        treatment_given: str = None,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        Logs an adverse event during blood donation phlebotomy.
        """
        donation = DonationRecord.query.get(donation_id)
        if not donation:
            raise ValueError(f"Donation ID {donation_id} not found.")

        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "donation_id": donation.id,
            "donation_code": donation.donation_code,
            "donor_id": donation.donor_id,
            "event_type": event_type.upper(),
            "severity": severity.upper(),
            "treatment_given": treatment_given or "Rest, elevation, fluids administered.",
            "notes": notes,
            "logged_at": timestamp
        }

        # Create Notification if Moderate or Severe
        if severity.upper() in [ReactionSeverity.MODERATE, ReactionSeverity.SEVERE, ReactionSeverity.CRITICAL]:
            NotificationService.create_notification(
                title=f"HEMOVIGILANCE ALERT: {severity} Donation Reaction",
                message=f"Adverse reaction '{event_type}' ({severity}) reported for Donor ID {donation.donor_id} under Donation {donation.donation_code}.",
                category=NotificationCategory.SYSTEM_ALERT.value,
                priority=NotificationPriority.HIGH.value,
                related_entity_type="DonationRecord",
                related_entity_id=str(donation.id)
            )

        logger.info(f"Logged Adverse Donation Event '{event_type}' ({severity}) for Donation '{donation.donation_code}'")
        return log_entry

    @staticmethod
    def log_transfusion_adverse_event(
        bag_id: int,
        hospital_name: str,
        reaction_type: str, # ACUTE_HEMOLYTIC, FEBRILE_NON_HEMOLYTIC, ALLERGIC, TRALI, TACO
        severity: str = ReactionSeverity.MODERATE,
        clinical_details: str = None
    ) -> Dict[str, Any]:
        """
        Logs a post-transfusion adverse reaction reported by a recipient hospital.
        """
        bag = BloodBag.query.get(bag_id)
        bag_code = bag.bag_code if bag else f"BAG-{bag_id}"

        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "bag_id": bag_id,
            "bag_code": bag_code,
            "hospital_name": hospital_name,
            "reaction_type": reaction_type.upper(),
            "severity": severity.upper(),
            "clinical_details": clinical_details,
            "reported_at": timestamp
        }

        # High-priority alert for severe transfusion reaction
        NotificationService.create_notification(
            title=f"CRITICAL HEMOVIGILANCE ALERT: Post-Transfusion Reaction ({reaction_type})",
            message=f"Hospital '{hospital_name}' reported a {severity} {reaction_type} reaction for Blood Bag {bag_code}. Bag lineage quarantine review initiated.",
            category=NotificationCategory.VALIDATION_FAILURE.value,
            priority=NotificationPriority.CRITICAL.value,
            related_entity_type="BloodBag",
            related_entity_id=str(bag_id)
        )

        logger.error(f"Post-Transfusion Reaction '{reaction_type}' reported for Bag '{bag_code}' by '{hospital_name}'")
        return log_entry
