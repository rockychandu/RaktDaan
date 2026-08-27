"""
Pydantic/Validator Schemas for Donation Workflow (Member 3).
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.common.constants import DonationType, DonationStatus


class DonationCreateSchema(BaseModel):
    donor_id: int = Field(..., description="Donor Profile ID")
    donation_type: str = Field(DonationType.WHOLE_BLOOD.value, description="Type of donation procedure")
    collection_center: str = Field("Central RaktDaan Blood Bank", min_length=2, max_length=150)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("donation_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = [t.value for t in DonationType]
        if v not in valid_types:
            raise ValueError(f"Donation type must be one of {valid_types}.")
        return v


class DonationScreeningUpdateSchema(BaseModel):
    weight_kg: float = Field(..., ge=30.0, le=200.0)
    hemoglobin_level: float = Field(..., ge=7.0, le=22.0)
    blood_pressure_sys: int = Field(..., ge=80, le=200)
    blood_pressure_dia: int = Field(..., ge=50, le=120)
    pulse_rate: int = Field(..., ge=50, le=140)
    temp_celsius: float = Field(36.5, ge=35.0, le=40.0)
    has_chronic_illness: bool = False
    is_on_medication: bool = False
    screening_notes: Optional[str] = Field(None, max_length=500)
    is_passed: bool = Field(..., description="Healthcare staff screening approval result")


class DonationStatusUpdateSchema(BaseModel):
    status: str = Field(..., description="Target status in donation workflow")
    cancellation_reason: Optional[str] = Field(None, max_length=255)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = [s.value for s in DonationStatus]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}.")
        return v
