"""
Pydantic Validation Schemas for Donor Health Checkup Pre-Screening.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HealthCheckupSchema(BaseModel):
    """
    Schema for donor self-checkup input.
    """
    weight_kg: float = Field(..., ge=30.0, le=200.0, description="Weight in kg")
    hemoglobin_level: float = Field(..., ge=5.0, le=22.0, description="Hemoglobin in g/dL")
    blood_pressure_sys: int = Field(..., ge=60, le=220, description="Systolic Blood Pressure (mmHg)")
    blood_pressure_dia: int = Field(..., ge=40, le=140, description="Diastolic Blood Pressure (mmHg)")
    pulse_rate: int = Field(..., ge=40, le=160, description="Pulse Rate (bpm)")
    temp_celsius: float = Field(36.6, ge=34.0, le=42.0, description="Body Temperature (°C)")
    has_chronic_illness: bool = Field(False, description="Has fever or illness in last 14 days")
    is_on_medication: bool = Field(False, description="Is currently on prescription medications")
    collection_center: Optional[str] = Field("Central RaktDaan Blood Bank", description="Chosen collection center")
