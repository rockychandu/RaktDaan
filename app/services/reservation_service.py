"""
Blood Reservation Engine & FEFO Bag Allocation Service (Member 4).
Performs FEFO (First-Expiring-First-Out) bag selection, enforces double-reservation prevention,
and manages reservation expiration and release.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.inventory_extended import BloodReservation
from app.common.constants import BloodBagStatus, UNIVERSAL_COMPATIBILITY_MAP, TransactionType
from app.common.exceptions import (
    InsufficientStockException, ReservationNotFoundException, ReservationConflictException
)
from app.services.inventory_service import InventoryService
from app.services.blood_bag_service import BloodBagService
from app.schemas.reservation_dispatch_schemas import ReservationCreateSchema

logger = logging.getLogger(__name__)


def generate_unique_reservation_code() -> str:
    """
    Generates unique reservation code in format RSV-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(BloodReservation).count() + 1
    return f"RSV-{year}-{count:06d}"


class ReservationService:
    """
    Business Logic Layer for Blood Bag Reservation & FEFO Selection.
    """

    @staticmethod
    def create_reservation(data_dict: Dict[str, Any], user_id: Optional[int] = None) -> BloodReservation:
        """
        Selects eligible AVAILABLE blood bags using FEFO strategy and reserves requested quantity.
        """
        schema = ReservationCreateSchema(**data_dict)

        # Determine compatible donor blood groups
        compatible_groups = UNIVERSAL_COMPATIBILITY_MAP.get(schema.blood_group, [schema.blood_group])

        # FEFO Selection Strategy: Query AVAILABLE bags ordered by expiry_date ASC
        available_bags = BloodBag.query.filter(
            BloodBag.blood_group.in_(compatible_groups),
            BloodBag.component_type == schema.component_type,
            BloodBag.status == BloodBagStatus.AVAILABLE.value,
            BloodBag.expiry_date > datetime.now(timezone.utc).date(),
            BloodBag.is_deleted == False
        ).order_by(BloodBag.expiry_date.asc()).limit(schema.quantity_units).all()

        if len(available_bags) < schema.quantity_units:
            raise InsufficientStockException(
                blood_group=schema.blood_group,
                requested_units=schema.quantity_units,
                available_units=len(available_bags)
            )

        rsv_code = generate_unique_reservation_code()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=schema.reservation_duration_hours)

        reservation = BloodReservation(
            reservation_code=rsv_code,
            reference_request_id=schema.reference_request_id,
            hospital_name=schema.hospital_name,
            patient_name=schema.patient_name,
            blood_group=schema.blood_group,
            component_type=schema.component_type,
            quantity_units=schema.quantity_units,
            status="ACTIVE",
            expires_at=expires_at,
            created_by_user_id=user_id,
            notes=schema.notes
        )

        # Transition bag statuses to RESERVED & associate
        for bag in available_bags:
            reservation.reserved_bags.append(bag)
            BloodBagService.transition_bag_status(
                bag_id=bag.id,
                target_status=BloodBagStatus.RESERVED.value,
                reason=f"Reserved for Reservation Code {rsv_code} (Hospital: {schema.hospital_name})",
                changed_by_user_id=user_id
            )

        db.session.add(reservation)
        db.session.commit()

        logger.info(f"Created Reservation '{rsv_code}': {schema.quantity_units} units of {schema.blood_group} reserved.")
        return reservation

    @staticmethod
    def release_reservation(reservation_id: int, reason: str = "Reservation Released", user_id: Optional[int] = None) -> BloodReservation:
        """
        Releases reserved bags back to AVAILABLE stock.
        """
        reservation = BloodReservation.query.filter_by(id=reservation_id, is_deleted=False).first()
        if not reservation:
            raise ReservationNotFoundException(reservation_id)

        if reservation.status != "ACTIVE":
            raise ReservationConflictException(reservation_id, f"Reservation is already in '{reservation.status}' status.")

        reservation.status = "RELEASED"

        for bag in reservation.reserved_bags:
            if bag.status == BloodBagStatus.RESERVED.value:
                BloodBagService.transition_bag_status(
                    bag_id=bag.id,
                    target_status=BloodBagStatus.AVAILABLE.value,
                    reason=f"Reservation {reservation.reservation_code} Released: {reason}",
                    changed_by_user_id=user_id
                )

        db.session.commit()
        logger.info(f"Released Reservation ID {reservation_id} ({reservation.reservation_code})")
        return reservation

    @staticmethod
    def check_and_release_expired_reservations() -> int:
        """
        Automated job to release reservations that have exceeded their expiration hold period.
        """
        now = datetime.now(timezone.utc)
        expired_reservations = BloodReservation.query.filter(
            BloodReservation.expires_at <= now,
            BloodReservation.status == "ACTIVE",
            BloodReservation.is_deleted == False
        ).all()

        released_count = 0
        for rsv in expired_reservations:
            rsv.status = "EXPIRED"
            for bag in rsv.reserved_bags:
                if bag.status == BloodBagStatus.RESERVED.value:
                    BloodBagService.transition_bag_status(
                        bag_id=bag.id,
                        target_status=BloodBagStatus.AVAILABLE.value,
                        reason=f"Automatic Reservation Expiry Timeout ({rsv.reservation_code})"
                    )
            released_count += 1

        db.session.commit()
        if released_count > 0:
            logger.info(f"Released {released_count} timed-out expired reservations.")
        return released_count
