"""
Hospital Return & Safety Recall Management Service Layer (Member 4).
Handles hospital returns, cold chain seal inspections, and final disposition.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.inventory_extended import BloodReturnRecall
from app.common.constants import BloodBagStatus
from app.common.exceptions import BloodBagNotFoundException
from app.services.blood_bag_service import BloodBagService
from app.schemas.quarantine_return_schemas import ReturnRecallCreateSchema

logger = logging.getLogger(__name__)


def generate_unique_return_code() -> str:
    """
    Generates unique return tracking code in format RET-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(BloodReturnRecall).count() + 1
    return f"RET-{year}-{count:06d}"


class ReturnRecallService:
    """
    Business Logic Layer for Returned & Recalled Blood Bags.
    """

    @staticmethod
    def process_return_or_recall(data_dict: Dict[str, Any], user_id: int) -> BloodReturnRecall:
        """
        Processes a returned blood bag and assigns immediate disposition.
        """
        schema = ReturnRecallCreateSchema(**data_dict)
        bag = BloodBagService.get_bag_by_id(schema.bag_id)

        ret_code = generate_unique_return_code()

        record = BloodReturnRecall(
            return_code=ret_code,
            bag_id=bag.id,
            return_source=schema.return_source,
            reason=schema.reason,
            inspection_notes=schema.inspection_notes,
            disposition=schema.disposition,
            processed_by_user_id=user_id
        )
        db.session.add(record)

        # Transition blood bag status according to disposition
        if schema.disposition == "RETURNED_TO_STOCK":
            target_status = BloodBagStatus.AVAILABLE.value
        elif schema.disposition == "DISCARDED":
            target_status = BloodBagStatus.DISCARDED.value
        else:
            target_status = BloodBagStatus.QUARANTINED.value

        BloodBagService.transition_bag_status(
            bag_id=bag.id,
            target_status=target_status,
            reason=f"Processed Hospital Return ({ret_code}): {schema.reason}. Disposition={schema.disposition}",
            changed_by_user_id=user_id
        )

        db.session.commit()
        logger.info(f"Processed Return '{ret_code}' for Bag '{bag.bag_code}' with Disposition '{schema.disposition}'")
        return record

    @staticmethod
    def list_returns() -> List[Dict[str, Any]]:
        """
        Lists all recorded hospital return events.
        """
        records = BloodReturnRecall.query.filter_by(is_deleted=False).order_by(BloodReturnRecall.return_date.desc()).all()
        return [r.to_dict() for r in records]
