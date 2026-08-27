"""
Admin Account Creation & Management Pydantic Validation Schemas.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class AdminCreateSchema(BaseModel):
    """
    Schema for creating a new Admin account with custom values.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Full Name of the Admin")
    email: EmailStr = Field(..., description="Unique Email Address")
    password: str = Field(..., min_length=8, description="Account Password")
    phone: str = Field(..., min_length=10, max_length=20, description="Contact Phone Number")
    role: str = Field("ADMIN", description="Role: ADMIN, SUPER_ADMIN, LAB_STAFF, INVENTORY_MANAGER")
    department: Optional[str] = Field("Blood Inventory", description="Department / Section")
    employee_id: Optional[str] = Field(None, description="Employee ID Code (e.g. EMP-2026-001)")

    @field_validator("role")
    def validate_role(cls, v):
        allowed = ["ADMIN", "SUPER_ADMIN", "LAB_STAFF", "INVENTORY_MANAGER"]
        val = v.upper().strip()
        if val not in allowed:
            raise ValueError(f"Invalid admin role '{v}'. Allowed roles: {', '.join(allowed)}")
        return val

    @field_validator("password")
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        return v
