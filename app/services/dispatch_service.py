"""
Hospital Dispatch Logistics & Workflow Service Layer (Member 4).
Executes dispatch workflow (RESERVED/AVAILABLE -> DISPATCHED), records cold chain parameters,
deducts inventory, and maintains audit ledger.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.inventory_extended import BloodDispatch, BloodReservation
from app.common.constants import BloodBagStatus, TransactionType
from app.common.exceptions import (
    BloodBagNotFoundException, ExpiredBagOperationException, QuarantinedBagOperationException, DispatchNotFoundException
)
from app.services.blood_bag_service import BloodBagService
from app.schemas.reservation_dispatch_schemas import DispatchCreateSchema

logger = logging.getLogger(__name__)


def generate_unique_dispatch_code() -> str:
    """
    Generates unique dispatch tracking code in format DSP-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(BloodDispatch).count() + 1
    return f"DSP-{year}-{count:06d}"


class DispatchService:
    """
    Business Logic Layer for Hospital Blood Bag Dispatches.
    """

    @staticmethod
    def create_dispatch(data_dict: Dict[str, Any], user_id: int) -> BloodDispatch:
        """
        Executes blood bag dispatch order for recipient hospital/patient.
        """
        schema = DispatchCreateSchema(**data_dict)

        # Validate provided blood bag IDs
        bags_to_dispatch = []
        for bag_id in schema.bag_ids:
            bag = BloodBag.query.filter_by(id=bag_id, is_deleted=False).first()
            if not bag:
                raise BloodBagNotFoundException(bag_id)
            if bag.status == BloodBagStatus.EXPIRED.value:
                raise ExpiredBagOperationException(bag.bag_code, "Dispatch")
            if bag.status == BloodBagStatus.QUARANTINED.value:
                raise QuarantinedBagOperationException(bag.bag_code, "Dispatch")
            bags_to_dispatch.append(bag)

        dsp_code = generate_unique_dispatch_code()

        dispatch = BloodDispatch(
            dispatch_code=dsp_code,
            reservation_id=schema.reservation_id,
            reference_request_id=schema.reference_request_id,
            hospital_name=schema.hospital_name,
            recipient_patient_name=schema.recipient_patient_name,
            blood_group=schema.blood_group,
            component_type=schema.component_type,
            quantity_units=len(bags_to_dispatch),
            dispatched_by_user_id=user_id,
            status="COMPLETED",
            transport_box_temp_celsius=schema.transport_box_temp_celsius,
            notes=schema.notes
        )

        # Update reservation status if linked
        if schema.reservation_id:
            reservation = BloodReservation.query.get(schema.reservation_id)
            if reservation:
                reservation.status = "DISPATCHED"

        # Transition bag statuses to DISPATCHED
        for bag in bags_to_dispatch:
            dispatch.dispatched_bags.append(bag)
            BloodBagService.transition_bag_status(
                bag_id=bag.id,
                target_status=BloodBagStatus.DISPATCHED.value,
                reason=f"Dispatched under Code {dsp_code} to Hospital '{schema.hospital_name}'",
                changed_by_user_id=user_id
            )

        db.session.add(dispatch)
        db.session.commit()

        logger.info(f"Dispatched Order '{dsp_code}': {len(bags_to_dispatch)} bags sent to {schema.hospital_name}")
        return dispatch

    @staticmethod
    def get_dispatch_by_id(dispatch_id: int) -> BloodDispatch:
        """
        Retrieves dispatch record by ID.
        """
        dispatch = BloodDispatch.query.filter_by(id=dispatch_id, is_deleted=False).first()
        if not dispatch:
            raise DispatchNotFoundException(dispatch_id)
        return dispatch

    @staticmethod
    def list_dispatches(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Lists and paginates hospital dispatches.
        """
        query = BloodDispatch.query.filter_by(is_deleted=False).order_by(BloodDispatch.dispatch_date.desc())
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": [d.to_dict() for d in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
