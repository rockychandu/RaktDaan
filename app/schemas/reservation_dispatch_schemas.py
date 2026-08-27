"""
Pydantic/Validator Schemas for Reservation & Dispatch Workflows (Member 4).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.users.models import BloodGroup
from app.common.constants import ComponentType


class ReservationCreateSchema(BaseModel):
    reference_request_id: str = Field(..., min_length=2, max_length=100, description="Hospital or Patient Request Ref")
    hospital_name: str = Field(..., min_length=2, max_length=150, description="Recipient Hospital Name")
    patient_name: str = Field(..., min_length=2, max_length=100, description="Patient Name")
    blood_group: str = Field(..., description="Target Blood Group")
    component_type: str = Field(ComponentType.WHOLE_BLOOD.value, description="Component Type")
    quantity_units: int = Field(..., ge=1, le=50, description="Units requested to reserve")
    reservation_duration_hours: int = Field(24, ge=1, le=168, description="Hold duration in hours")
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


class DispatchCreateSchema(BaseModel):
    reservation_id: Optional[int] = Field(None, description="Linked Reservation ID (if pre-reserved)")
    reference_request_id: str = Field(..., min_length=2, max_length=100, description="Hospital Request Code")
    hospital_name: str = Field(..., min_length=2, max_length=150, description="Recipient Hospital Name")
    recipient_patient_name: str = Field(..., min_length=2, max_length=100, description="Patient Name")
    blood_group: str = Field(..., description="Blood Group")
    component_type: str = Field(ComponentType.WHOLE_BLOOD.value, description="Component Type")
    bag_ids: List[int] = Field(..., min_items=1, max_items=50, description="List of Blood Bag IDs to Dispatch")
    transport_box_temp_celsius: Optional[float] = Field(4.0, ge=-40.0, le=30.0, description="Cold Chain Transport Temp")
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        valid_bgs = [bg.value for bg in BloodGroup]
        if v not in valid_bgs:
            raise ValueError(f"Blood group must be one of {valid_bgs}.")
        return v
