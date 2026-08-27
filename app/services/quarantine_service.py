"""
Quarantine & Safety Isolation Service Layer (Member 4).
Places blood bags into quarantine, excludes them from available stock, and handles authorized resolutions.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.inventory_extended import QuarantineRecord
from app.common.constants import BloodBagStatus, NotificationCategory, NotificationPriority
from app.common.exceptions import BloodBagNotFoundException, QuarantineNotFoundException
from app.services.blood_bag_service import BloodBagService
from app.services.notification_service import NotificationService
from app.schemas.quarantine_return_schemas import QuarantineCreateSchema, QuarantineResolveSchema

logger = logging.getLogger(__name__)


def generate_unique_quarantine_code() -> str:
    """
    Generates unique quarantine tracking code in format QRN-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(QuarantineRecord).count() + 1
    return f"QRN-{year}-{count:06d}"


class QuarantineService:
    """
    Business Logic Layer for Blood Bag Quarantine & Safety Isolation.
    """

    @staticmethod
    def place_bag_in_quarantine(data_dict: Dict[str, Any], user_id: int) -> QuarantineRecord:
        """
        Moves a blood bag into QUARANTINED status and creates quarantine audit record.
        """
        schema = QuarantineCreateSchema(**data_dict)
        bag = BloodBagService.get_bag_by_id(schema.bag_id)

        qrn_code = generate_unique_quarantine_code()

        record = QuarantineRecord(
            quarantine_code=qrn_code,
            bag_id=bag.id,
            reason=schema.reason,
            suspected_issue=schema.suspected_issue,
            quarantined_by_user_id=user_id,
            status="ACTIVE"
        )
        db.session.add(record)

        # Transition bag to QUARANTINED status
        BloodBagService.transition_bag_status(
            bag_id=bag.id,
            target_status=BloodBagStatus.QUARANTINED.value,
            reason=f"Placed in Quarantine ({qrn_code}): {schema.reason}",
            changed_by_user_id=user_id
        )

        # Trigger internal alert
        NotificationService.create_notification(
            title=f"Quarantine Isolation Alert: {bag.bag_code}",
            message=f"Blood bag {bag.bag_code} ({bag.blood_group}) moved to QUARANTINE. Reason: {schema.reason}",
            category=NotificationCategory.QUARANTINE_ALERT.value,
            priority=NotificationPriority.HIGH.value,
            related_entity_type="QuarantineRecord",
            related_entity_id=qrn_code
        )

        db.session.commit()
        logger.info(f"Quarantined Bag '{bag.bag_code}' under Code '{qrn_code}'")
        return record

    @staticmethod
    def resolve_quarantine(quarantine_id: int, data_dict: Dict[str, Any], user_id: int) -> QuarantineRecord:
        """
        Resolves quarantine record by returning bag to AVAILABLE or DISCARDING it.
        """
        record = QuarantineRecord.query.filter_by(id=quarantine_id, is_deleted=False).first()
        if not record:
            raise QuarantineNotFoundException(quarantine_id)

        schema = QuarantineResolveSchema(**data_dict)
        bag = record.blood_bag

        if schema.resolution == "RELEASE_TO_AVAILABLE":
            record.status = "RESOLVED_RELEASED"
            target_status = BloodBagStatus.AVAILABLE.value
            reason_msg = f"Quarantine {record.quarantine_code} Resolved & Released: {schema.resolution_notes}"
        else:
            record.status = "RESOLVED_DISCARDED"
            target_status = BloodBagStatus.DISCARDED.value
            reason_msg = f"Quarantine {record.quarantine_code} Resolved & Discarded: {schema.resolution_notes}"

        record.resolution_notes = schema.resolution_notes
        record.resolved_at = datetime.now(timezone.utc)
        record.resolved_by_user_id = user_id

        if bag and bag.status == BloodBagStatus.QUARANTINED.value:
            BloodBagService.transition_bag_status(
                bag_id=bag.id,
                target_status=target_status,
                reason=reason_msg,
                changed_by_user_id=user_id
            )

        db.session.commit()
        logger.info(f"Resolved Quarantine ID {quarantine_id}: Resolution={schema.resolution}")
        return record

    @staticmethod
    def list_active_quarantines() -> List[Dict[str, Any]]:
        """
        Lists all currently active quarantined blood bags.
        """
        records = QuarantineRecord.query.filter_by(status="ACTIVE", is_deleted=False).all()
        return [r.to_dict() for r in records]
