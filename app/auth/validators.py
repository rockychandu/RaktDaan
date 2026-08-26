import re
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from app.users.models import BloodGroup, UserRole

class DonorRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: str = Field(..., description="Valid Email Address")
    phone: str = Field(..., description="Phone Number")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Password Confirmation")
    date_of_birth: date = Field(..., description="Date of Birth (YYYY-MM-DD)")
    gender: str = Field(..., description="Gender (Male/Female/Other)")
    blood_group: str = Field(..., description="Blood Group e.g. A+, O-")
    address: str = Field(..., min_length=3, max_length=255, description="Street Address")
    city: str = Field(..., min_length=2, max_length=100, description="City")
    state: str = Field(..., min_length=2, max_length=100, description="State")
    emergency_contact: str = Field(..., description="Emergency Contact Phone Number")

    @field_validator("name", "address", "city", "state")
    @classmethod
    def validate_non_empty_strings(cls, v: str, info) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError(f"{info.field_name} cannot be empty or whitespace only.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v_clean = v.strip().lower()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v_clean):
            raise ValueError("Invalid email format.")
        return v_clean

    @field_validator("phone", "emergency_contact")
    @classmethod
    def validate_phone_number(cls, v: str, info) -> str:
        v_clean = v.strip()
        # Accept optional + prefix and 10 to 15 digits
        pattern = r"^\+?[0-9]{10,15}$"
        if not re.match(pattern, v_clean):
            raise ValueError(f"Invalid {info.field_name}. Must contain 10-15 digits.")
        return v_clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Date of birth must be in the past.")
        
        # Calculate age
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Donor must be at least 18 years old.")
        if age > 100:
            raise ValueError("Invalid date of birth.")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        v_clean = v.strip().capitalize()
        allowed = ["Male", "Female", "Other"]
        if v_clean not in allowed:
            raise ValueError(f"Gender must be one of: {', '.join(allowed)}")
        return v_clean

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        v_clean = v.strip().upper()
        allowed_groups = BloodGroup.list_values()
        if v_clean not in allowed_groups:
            raise ValueError(f"Invalid blood group. Must be one of: {', '.join(allowed_groups)}")
        return v_clean

    @model_validator(mode="after")
    def validate_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and Confirm Password do not match.")
        return self


class DonorProfileResponse(BaseModel):
    id: int
    date_of_birth: date
    gender: str
    blood_group: str
    address: str
    city: str
    state: str
    emergency_contact: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    status: str
    donor_profile: Optional[DonorProfileResponse] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str = Field(..., description="User Email")
    password: str = Field(..., description="Password")

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: UserResponse
