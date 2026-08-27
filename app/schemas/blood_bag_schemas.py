"""
Pydantic/Validator Schemas for Blood Bag Lifecycle & Component Management (Member 4).
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.common.constants import ComponentType, BloodBagStatus
from app.users.models import BloodGroup


class BloodBagCreateSchema(BaseModel):
    donation_id: Optional[int] = Field(None, description="Linked Donation Record ID")
    donor_id: Optional[int] = Field(None, description="Donor Profile ID")
    blood_group: str = Field(..., description="Human Blood Group")
    component_type: str = Field(ComponentType.WHOLE_BLOOD.value, description="Blood Component Type")
    volume_ml: int = Field(450, ge=10, le=1000, description="Volume in Milliliters")
    storage_unit_id: Optional[int] = Field(None, description="Assigned Storage Unit ID")
    shelf_position: Optional[str] = Field(None, max_length=50, description="Rack/Shelf/Position Designation")
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        valid_bgs = [bg.value for bg in BloodGroup]
        if v not in valid_bgs:
            raise ValueError(f"Blood group must be one of {valid_bgs}.")
        return v

    @field_validator("component_type")
    @classmethod
    def validate_component_type(cls, v: str) -> str:
        valid_comps = [c.value for c in ComponentType]
        if v not in valid_comps:
            raise ValueError(f"Component type must be one of {valid_comps}.")
        return v


class BloodBagStatusUpdateSchema(BaseModel):
    status: str = Field(..., description="Target status state")
    reason: str = Field(..., min_length=3, max_length=255, description="Reason for status change")
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = [s.value for s in BloodBagStatus]
        if v not in valid_statuses:
            raise ValueError(f"Blood bag status must be one of {valid_statuses}.")
        return v


class BloodBagSearchFilterSchema(BaseModel):
    bag_code: Optional[str] = Field(None, description="Unique Bag Code search")
    blood_group: Optional[str] = None
    component_type: Optional[str] = None
    status: Optional[str] = None
    storage_unit_id: Optional[int] = None
    expiring_within_days: Optional[int] = Field(None, ge=1, le=365)
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field("expiry_date")
    sort_order: str = Field("asc")
