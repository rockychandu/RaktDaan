"""
Donation State Machine & Life-Cycle State Transition Engine.
Enforces valid state transitions across all 12 donation states:
SCREENING_COMPLETED -> ELIGIBLE -> WAITING_FOR_STAFF -> APPROVED -> COLLECTION_PENDING ->
COLLECTED -> PROCESSING -> TESTING -> COMPLETED (or DEFERRED / REJECTED / CANCELLED).
"""

import logging
from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.donation import DonationRecord, DonationScreening
from app.database.models.blood_bank import BloodBag
from app.database.models.history_audit import DonorHistoryTimeline
from app.database.models.notification import InternalNotification
from app.common.constants import (
    DonationStatus, BloodBagStatus, ComponentType,
    NotificationCategory, NotificationPriority
)

logger = logging.getLogger(__name__)


class DonationStateMachine:
    """
    Finite State Machine managing donation lifecycles and historical timeline events.
    """

    VALID_TRANSITIONS = {
        "SCREENING_COMPLETED": ["ELIGIBLE", "DEFERRED", "CANCELLED"],
        "ELIGIBLE": ["WAITING_FOR_STAFF", "DEFERRED", "CANCELLED"],
        "WAITING_FOR_STAFF": ["APPROVED", "REJECTED", "CANCELLED"],
        "APPROVED": ["COLLECTION_PENDING", "CANCELLED"],
        "COLLECTION_PENDING": ["COLLECTED", "CANCELLED"],
        "COLLECTED": ["PROCESSING", "REJECTED"],
        "PROCESSING": ["TESTING", "REJECTED"],
        "TESTING": ["COMPLETED", "REJECTED"],
        "COMPLETED": [],
        "DEFERRED": [],
        "REJECTED": [],
        "CANCELLED": []
    }

    @classmethod
    def transition(
        cls,
        donation_id: int,
        target_status: str,
        staff_user_id: Optional[int] = None,
        remarks: Optional[str] = None,
        volume_ml: int = 450
    ) -> Dict[str, Any]:
        """
        Executes state transition, logs history timeline event, and updates inventory.
        """
        donation = DonationRecord.query.get(donation_id)
        if not donation:
            raise ValueError(f"Donation Record ID {donation_id} not found.")

        current = donation.donation_status.upper()
        target = target_status.upper()

        if target not in cls.VALID_TRANSITIONS.get(current, []):
            raise ValueError(f"Invalid transition from state '{current}' to '{target}'. Allowed target states: {cls.VALID_TRANSITIONS.get(current, [])}")

        donation.donation_status = target
        if staff_user_id:
            donation.staff_user_id = staff_user_id

        bag_code = None
        created_bag_id = None

        # Automatic Inventory Bag Creation when state transitions to COLLECTED or COMPLETED
        if target == "COLLECTED" and not donation.blood_bags:
            col_date = date.today()
            exp_date = col_date + timedelta(days=35)
            bag = BloodBag(
                bag_code=f"BB-2026-{donation.id:06d}",
                donation_id=donation.id,
                donor_id=donation.donor_id,
                blood_group=donation.blood_group,
                component_type=ComponentType.WHOLE_BLOOD.value,
                volume_ml=volume_ml,
                collection_date=col_date,
                processing_date=col_date,
                testing_date=col_date,
                expiry_date=exp_date,
                status=BloodBagStatus.AVAILABLE.value,
                quality_status="PASSED"
            )
            db.session.add(bag)
            db.session.flush()
            bag_code = bag.bag_code
            created_bag_id = bag.id

        # Record History Timeline Event
        history = DonorHistoryTimeline(
            donor_id=donation.donor_id,
            event_type=f"STATE_TRANSITION_{target}",
            event_date=datetime.now(timezone.utc),
            health_checkup_result=donation.screening_status,
            eligibility_status="ELIGIBLE" if target not in ["DEFERRED", "REJECTED", "CANCELLED"] else "TEMPORARILY_DEFERRED",
            reasons_summary=remarks or f"Transitioned to {target}",
            donation_id=donation.id,
            blood_bag_id=created_bag_id,
            blood_bag_code=bag_code,
            donation_status=target,
            staff_verifier_user_id=staff_user_id,
            staff_verification_status="VERIFIED" if staff_user_id else "UNVERIFIED",
            remarks=remarks
        )
        db.session.add(history)
        db.session.commit()

        logger.info(f"Donation ID {donation_id} transitioned from '{current}' to '{target}' (Bag: {bag_code})")
        return {
            "donation_id": donation.id,
            "previous_status": current,
            "new_status": target,
            "blood_bag_code": bag_code,
            "timeline_id": history.id
        }
