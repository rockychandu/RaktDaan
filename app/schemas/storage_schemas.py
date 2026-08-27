"""
Pydantic/Validator Schemas for Blood Storage Hierarchy & Capacity Management (Member 4).
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.common.constants import StorageType


class StorageUnitCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Storage Unit Name/Identifier")
    unit_type: str = Field(StorageType.BLOOD_REFRIGERATOR.value, description="Storage Unit Hardware Type")
    section_location: str = Field(..., min_length=2, max_length=100, description="Section / Room Location")
    total_capacity_units: int = Field(..., ge=1, le=10000, description="Total Bag Storage Capacity")
    min_temp_celsius: float = Field(..., ge=-100.0, le=40.0)
    max_temp_celsius: float = Field(..., ge=-100.0, le=40.0)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("unit_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = [t.value for t in StorageType]
        if v not in valid_types:
            raise ValueError(f"Storage unit type must be one of {valid_types}.")
        return v


class StorageLocationAssignSchema(BaseModel):
    bag_id: int = Field(..., description="Target Blood Bag ID")
    storage_unit_id: int = Field(..., description="Target Storage Unit ID")
    rack_number: Optional[str] = Field("Rack-1", max_length=50)
    shelf_number: Optional[str] = Field("Shelf-1", max_length=50)
    position_number: Optional[str] = Field("Pos-1", max_length=50)
    reason: Optional[str] = Field("Initial Storage Assignment", max_length=255)
