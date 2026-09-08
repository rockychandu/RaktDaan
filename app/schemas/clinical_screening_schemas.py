"""
Pydantic Validation Schemas for Clinical Screening, Health Checkup, and Admin Workflow Transitions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ComprehensiveHealthCheckupSchema(BaseModel):
    """
    Validation schema for full donor health checkup questionnaire.
    """
    weight_kg: float = Field(..., ge=30.0, le=200.0, description="Body weight in kg")
    hemoglobin_level: float = Field(..., ge=5.0, le=22.0, description="Hemoglobin level in g/dL")
    blood_pressure_sys: int = Field(..., ge=60, le=220, description="Systolic Blood Pressure (mmHg)")
    blood_pressure_dia: int = Field(..., ge=40, le=140, description="Diastolic Blood Pressure (mmHg)")
    pulse_rate: int = Field(..., ge=40, le=160, description="Resting Pulse Rate (bpm)")
    temp_celsius: float = Field(36.6, ge=34.0, le=42.0, description="Body Temperature (°C)")
    
    # Declarations
    has_chronic_illness: bool = Field(False, description="Fever or illness in last 14 days")
    is_on_medication: bool = Field(False, description="Currently taking prescription medication")
    has_recent_infection: bool = Field(False, description="Recent infection reported")
    has_recent_hospitalization: bool = Field(False, description="Recent hospitalization within 6 months")
    has_recent_surgery: bool = Field(False, description="Recent surgical procedure reported")
    surgery_type: Optional[str] = Field("NONE", description="MAJOR or MINOR surgery")
    medication_category: Optional[str] = Field("GENERAL", description="Medication category")
    has_recent_vaccination: bool = Field(False, description="Recent vaccination reported")
    vaccine_type: Optional[str] = Field("INACTIVATED", description="LIVE_ATTENUATED or INACTIVATED vaccine")
    is_currently_pregnant: bool = Field(False, description="Is currently pregnant")
    is_breastfeeding: bool = Field(False, description="Is actively breastfeeding")
    recent_delivery_within_12_months: bool = Field(False, description="Childbirth within last 12 months")
    collection_center: Optional[str] = Field("Central RaktDaan Blood Bank", description="Collection center")


class StateTransitionSchema(BaseModel):
    """
    Validation schema for admin donation state transitions.
    """
    donation_id: int = Field(..., gt=0, description="Donation Record ID")
    target_status: str = Field(..., description="Target donation status string")
    remarks: Optional[str] = Field("Updated by staff", description="Audit transition remarks")
    volume_ml: Optional[int] = Field(450, ge=200, le=600, description="Collected blood volume ml")
