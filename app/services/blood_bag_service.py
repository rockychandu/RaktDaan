"""
Blood Bag Lifecycle, State Machine & Traceability Service Layer (Member 4).
Generates unique Bag IDs (BB-2026-XXXXXX), enforces valid state transitions,
logs transition history, and produces visual/chronological tracking timelines.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Tuple, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.donation import DonationRecord
from app.database.models.inventory_extended import BloodBagStatusLog, StorageUnit
from app.common.constants import (
    BloodBagStatus, VALID_BAG_TRANSITIONS, COMPONENT_SHELF_LIFE_DAYS, ComponentType
)
from app.common.exceptions import (
    BloodBagNotFoundException, InvalidBagStatusTransition, ExpiredBagOperationException, QuarantinedBagOperationException
)
from app.schemas.blood_bag_schemas import BloodBagCreateSchema, BloodBagStatusUpdateSchema, BloodBagSearchFilterSchema

logger = logging.getLogger(__name__)


def generate_unique_bag_code() -> str:
    """
    Generates unique Blood Bag Barcode ID in format BB-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(BloodBag).count() + 1
    return f"BB-{year}-{count:06d}"


class BloodBagService:
    """
    Business Logic Engine for Blood Bag Lifecycle Management.
    """

    @staticmethod
    def create_blood_bag_from_donation(donation_id: int, volume_ml: int = 450, component_type: str = ComponentType.WHOLE_BLOOD.value) -> BloodBag:
        """
        Creates a new BloodBag entity directly from a completed donation event.
        """
        donation = DonationRecord.query.filter_by(id=donation_id).first()
        if not donation:
            raise ValueError(f"Donation record '{donation_id}' not found.")

        collection_date = donation.donation_date.date() if isinstance(donation.donation_date, datetime) else date.today()
        shelf_days = COMPONENT_SHELF_LIFE_DAYS.get(component_type, 35)
        expiry_date = collection_date + timedelta(days=shelf_days)

        bag_code = generate_unique_bag_code()

        bag = BloodBag(
            bag_code=bag_code,
            donation_id=donation.id,
            donor_id=donation.donor_id,
            blood_group=donation.blood_group,
            component_type=component_type,
            volume_ml=volume_ml,
            collection_date=collection_date,
            expiry_date=expiry_date,
            status=BloodBagStatus.COLLECTED.value,
            quality_status="UNTESTED"
        )
        db.session.add(bag)
        db.session.flush()

        # Log initial creation state
        log = BloodBagStatusLog(
            bag_id=bag.id,
            previous_status="NEW",
            new_status=BloodBagStatus.COLLECTED.value,
            reason="Blood bag collected from voluntary donation event."
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Created BloodBag '{bag_code}' for Donation ID {donation_id}")
        return bag

    @staticmethod
    def get_bag_by_id(bag_id: int) -> BloodBag:
        """
        Retrieves blood bag by primary key ID.
        """
        bag = BloodBag.query.filter_by(id=bag_id, is_deleted=False).first()
        if not bag:
            raise BloodBagNotFoundException(bag_id)
        return bag

    @staticmethod
    def get_bag_by_code(bag_code: str) -> BloodBag:
        """
        Retrieves blood bag by barcode code string.
        """
        bag = BloodBag.query.filter_by(bag_code=bag_code.strip(), is_deleted=False).first()
        if not bag:
            raise BloodBagNotFoundException(bag_code)
        return bag

    @staticmethod
    def transition_bag_status(
        bag_id: int,
        target_status: str,
        reason: str,
        changed_by_user_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> BloodBag:
        """
        Validates and executes a state transition for a blood bag.
        Updates aggregate inventory counts accordingly.
        """
        bag = BloodBagService.get_bag_by_id(bag_id)
        current_status = bag.status

        if target_status not in BloodBagStatus.list_values():
            raise ValueError(f"Invalid target status '{target_status}'.")

        # Validate transition matrix
        allowed_targets = VALID_BAG_TRANSITIONS.get(current_status, [])
        if target_status not in allowed_targets:
            raise InvalidBagStatusTransition(current_status, target_status)

        bag.status = target_status
        if target_status == BloodBagStatus.PROCESSING.value:
            bag.processing_date = date.today()
        elif target_status == BloodBagStatus.TESTING.value:
            bag.testing_date = date.today()

        # Log status transition
        log = BloodBagStatusLog(
            bag_id=bag.id,
            previous_status=current_status,
            new_status=target_status,
            changed_by_user_id=changed_by_user_id,
            reason=reason,
            notes=notes
        )
        db.session.add(log)

        # Import Inventory Service to update aggregate counts
        from app.services.inventory_service import InventoryService
        InventoryService.recalculate_aggregate_inventory_for_blood_group(bag.blood_group)

        # Import Transaction Service to log inventory transaction
        from app.services.inventory_transaction_service import InventoryTransactionService
        InventoryTransactionService.record_transaction(
            bag_id=bag.id,
            blood_group=bag.blood_group,
            component_type=bag.component_type,
            quantity_units=1,
            transaction_type=target_status,
            previous_status=current_status,
            new_status=target_status,
            performed_by_user_id=changed_by_user_id,
            reason=reason,
            notes=notes
        )

        db.session.commit()
        logger.info(f"Transitioned Bag '{bag.bag_code}' from '{current_status}' to '{target_status}'")
        return bag

    @staticmethod
    def get_bag_traceability_timeline(bag_id: int) -> Dict[str, Any]:
        """
        Generates full chronological traceability timeline for a blood bag.
        Donor -> Donation -> Collection -> Testing -> Storage -> Reservation -> Dispatch / Expiry.
        """
        bag = BloodBagService.get_bag_by_id(bag_id)
        logs = BloodBagStatusLog.query.filter_by(bag_id=bag.id).order_by(BloodBagStatusLog.created_at.asc()).all()

        timeline = []
        # Step 1: Donor & Collection Event
        donor_name = bag.donor_profile.user.name if (bag.donor_profile and bag.donor_profile.user) else "Anonymous"
        timeline.append({
            "stage": "DONATION_COLLECTION",
            "title": "Blood Donation Collected",
            "date": bag.collection_date.isoformat(),
            "details": f"Collected {bag.volume_ml} mL of {bag.blood_group} ({bag.component_type}) from Donor {donor_name}."
        })

        # Step 2: Processing & Testing
        if bag.testing_date:
            timeline.append({
                "stage": "TESTING_LAB",
                "title": "Laboratory Serology & Nucleic Acid Testing",
                "date": bag.testing_date.isoformat(),
                "details": f"Quality status marked as {bag.quality_status}."
            })

        # Step 3: Status Transition Log entries
        for log in logs:
            timeline.append({
                "stage": log.new_status,
                "title": f"Status Transition to {log.new_status}",
                "date": log.created_at.isoformat() if log.created_at else None,
                "details": f"Reason: {log.reason}. (Previous: {log.previous_status})"
            })

        # Step 4: Storage Location
        if bag.storage_unit:
            timeline.append({
                "stage": "STORAGE_ASSIGNMENT",
                "title": "Assigned Storage Location",
                "date": bag.updated_at.isoformat() if bag.updated_at else None,
                "details": f"Stored in '{bag.storage_unit.name}' (Position: {bag.shelf_position or 'Rack-1'})."
            })

        return {
            "bag_id": bag.id,
            "bag_code": bag.bag_code,
            "blood_group": bag.blood_group,
            "component_type": bag.component_type,
            "volume_ml": bag.volume_ml,
            "current_status": bag.status,
            "expiry_date": bag.expiry_date.isoformat(),
            "timeline": timeline
        }

    @staticmethod
    def search_blood_bags(filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Searches, filters, and paginates blood bags.
        """
        schema = BloodBagSearchFilterSchema(**filter_params)

        query = BloodBag.query.filter_by(is_deleted=False)

        if schema.bag_code:
            query = query.filter(BloodBag.bag_code.ilike(f"%{schema.bag_code.strip()}%"))
        if schema.blood_group:
            query = query.filter(BloodBag.blood_group == schema.blood_group)
        if schema.component_type:
            query = query.filter(BloodBag.component_type == schema.component_type)
        if schema.status:
            query = query.filter(BloodBag.status == schema.status)
        if schema.storage_unit_id:
            query = query.filter(BloodBag.storage_unit_id == schema.storage_unit_id)
        if schema.expiring_within_days:
            cutoff = date.today() + timedelta(days=schema.expiring_within_days)
            query = query.filter(BloodBag.expiry_date <= cutoff, BloodBag.status == BloodBagStatus.AVAILABLE.value)

        # Sorting
        if schema.sort_by == "collection_date":
            sort_col = BloodBag.collection_date
        elif schema.sort_by == "blood_group":
            sort_col = BloodBag.blood_group
        else:
            sort_col = BloodBag.expiry_date

        if schema.sort_order.lower() == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        total = query.count()
        bags = query.offset((schema.page - 1) * schema.per_page).limit(schema.per_page).all()

        return {
            "items": [b.to_dict() for b in bags],
            "total": total,
            "page": schema.page,
            "per_page": schema.per_page,
            "total_pages": (total + schema.per_page - 1) // schema.per_page
        }
