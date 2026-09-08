"""
Storage Location Hierarchy & Capacity Management Service Layer (Member 4).
Manages 5-level storage hierarchy (Blood Bank -> Unit -> Rack -> Shelf -> Position),
prevents over-capacity, assigns blood bags to cold units, and handles relocation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.inventory_extended import StorageUnit, StorageLocation
from app.common.exceptions import (
    StorageUnitNotFoundException, StorageCapacityExceededException, BloodBagNotFoundException
)
from app.schemas.storage_schemas import StorageUnitCreateSchema, StorageLocationAssignSchema

logger = logging.getLogger(__name__)


class StorageService:
    """
    Business Logic Layer for Blood Bank Storage Equipment & Location Assignment.
    """

    @staticmethod
    def create_storage_unit(data_dict: Dict[str, Any]) -> StorageUnit:
        """
        Creates a new cold storage equipment unit.
        """
        schema = StorageUnitCreateSchema(**data_dict)
        unit = StorageUnit(
            name=schema.name,
            unit_type=schema.unit_type,
            section_location=schema.section_location,
            total_capacity_units=schema.total_capacity_units,
            occupied_units=0,
            min_temp_celsius=schema.min_temp_celsius,
            max_temp_celsius=schema.max_temp_celsius,
            notes=schema.notes
        )
        db.session.add(unit)
        db.session.commit()
        logger.info(f"Created StorageUnit ID {unit.id}: '{unit.name}' (Capacity: {unit.total_capacity_units})")
        return unit

    @staticmethod
    def get_unit_by_id(unit_id: int) -> StorageUnit:
        """
        Retrieves storage unit by ID.
        """
        unit = StorageUnit.query.filter_by(id=unit_id, is_deleted=False).first()
        if not unit:
            raise StorageUnitNotFoundException(unit_id)
        return unit

    @staticmethod
    def assign_bag_to_storage_location(data_dict: Dict[str, Any]) -> Tuple[BloodBag, StorageUnit]:
        """
        Assigns a blood bag to a storage unit and location position.
        Prevents over-capacity.
        """
        schema = StorageLocationAssignSchema(**data_dict)
        bag = BloodBag.query.filter_by(id=schema.bag_id, is_deleted=False).first()
        if not bag:
            raise BloodBagNotFoundException(schema.bag_id)

        unit = StorageService.get_unit_by_id(schema.storage_unit_id)

        # Over-capacity check
        if unit.occupied_units >= unit.total_capacity_units:
            raise StorageCapacityExceededException(unit.name, unit.total_capacity_units, unit.occupied_units)

        # Handle previous storage unit un-assignment if relocated
        if bag.storage_unit_id and bag.storage_unit_id != unit.id:
            prev_unit = StorageUnit.query.get(bag.storage_unit_id)
            if prev_unit and prev_unit.occupied_units > 0:
                prev_unit.occupied_units -= 1

        bag.storage_unit_id = unit.id
        bag.shelf_position = f"{schema.rack_number} / {schema.shelf_number} / {schema.position_number}"

        unit.occupied_units += 1

        # Create StorageLocation record
        loc = StorageLocation(
            storage_unit_id=unit.id,
            rack_number=schema.rack_number,
            shelf_number=schema.shelf_number,
            position_number=schema.position_number,
            is_occupied=True,
            assigned_bag_id=bag.id
        )
        db.session.add(loc)

        db.session.commit()
        logger.info(f"Assigned Bag '{bag.bag_code}' to Unit '{unit.name}' at position '{bag.shelf_position}'")
        return bag, unit

    @staticmethod
    def list_storage_units() -> List[Dict[str, Any]]:
        """
        Lists all storage units with current occupied & available capacity.
        """
        units = StorageUnit.query.filter_by(is_deleted=False).all()
        return [u.to_dict() for u in units]
