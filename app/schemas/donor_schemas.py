"""
Pydantic/Validator Schemas for Donor Management (Member 3).
Handles donor registration, profile update, medical questionnaire, eligibility request validation.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from app.users.models import BloodGroup, Gender, EligibilityStatus


class DonorRegistrationSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    phone: str = Field(..., min_length=10, max_length=15, description="Primary Phone Number")
    date_of_birth: date = Field(..., description="Date of Birth (YYYY-MM-DD)")
    gender: str = Field(..., description="Gender (Male, Female, Other)")
    blood_group: str = Field(..., description="Blood Group (A+, A-, B+, B-, AB+, AB-, O+, O-)")
    address: str = Field(..., min_length=5, max_length=255, description="Street Address")
    city: str = Field(..., min_length=2, max_length=100, description="City")
    state: str = Field(..., min_length=2, max_length=100, description="State")
    emergency_contact: str = Field(..., min_length=10, max_length=15, description="Emergency Contact Phone")

    @field_validator("phone", "emergency_contact")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
        if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Phone number must contain between 10 and 15 digits.")
        return cleaned

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        valid_genders = [g.value for g in Gender]
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of {valid_genders}.")
        return v

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        valid_bgs = [bg.value for bg in BloodGroup]
        if v not in valid_bgs:
            raise ValueError(f"Blood group must be one of {valid_bgs}.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, dob: date) -> date:
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18 or age > 65:
            raise ValueError(f"Donor age must be between 18 and 65 years old (calculated age: {age}).")
        return dob


class DonorUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    emergency_contact: Optional[str] = Field(None, min_length=10, max_length=15)
    blood_group: Optional[str] = None
    gender: Optional[str] = None

    @field_validator("phone", "emergency_contact")
    @classmethod
    def validate_optional_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
        if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Phone number must contain between 10 and 15 digits.")
        return cleaned


class DonorMedicalHistorySchema(BaseModel):
    weight_kg: float = Field(..., ge=30.0, le=250.0, description="Weight in KG")
    hemoglobin_level: Optional[float] = Field(None, ge=5.0, le=25.0, description="Hemoglobin in g/dL")
    blood_pressure_sys: Optional[int] = Field(None, ge=70, le=220, description="Systolic Blood Pressure")
    blood_pressure_dia: Optional[int] = Field(None, ge=40, le=140, description="Diastolic Blood Pressure")
    pulse_rate: Optional[int] = Field(None, ge=40, le=180, description="Pulse Rate (BPM)")
    has_chronic_illness: bool = Field(False, description="Chronic Illness Flag")
    is_on_medication: bool = Field(False, description="Current Medication Flag")
    medical_notes: Optional[str] = Field(None, max_length=1000, description="Additional Screening Notes")


class DonorSearchFilterSchema(BaseModel):
    query: Optional[str] = Field(None, description="Search term for name, code, phone, or email")
    blood_group: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    eligibility_status: Optional[str] = None
    is_active: Optional[bool] = True
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at")
    sort_order: str = Field("desc")
