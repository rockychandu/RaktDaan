"""
Pydantic/Validator Schemas for Inventory Thresholds & Transactions (Member 4).
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.users.models import BloodGroup


class StockThresholdUpdateSchema(BaseModel):
    blood_group: str = Field(..., description="Human Blood Group")
    minimum_units: int = Field(..., ge=1, le=1000, description="Low Stock Alert Threshold")
    critical_units: int = Field(..., ge=1, le=1000, description="Critical Stock Alert Threshold")

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v: str) -> str:
        valid_bgs = [bg.value for bg in BloodGroup]
        if v not in valid_bgs:
            raise ValueError(f"Blood group must be one of {valid_bgs}.")
        return v

    @field_validator("critical_units")
    @classmethod
    def validate_critical_less_than_min(cls, v: int, info) -> int:
        if "minimum_units" in info.data and v >= info.data["minimum_units"]:
            raise ValueError("Critical stock threshold must be strictly less than minimum stock threshold.")
        return v


class InventoryTransactionFilterSchema(BaseModel):
    blood_group: Optional[str] = None
    transaction_type: Optional[str] = None
    bag_code: Optional[str] = None
    user_id: Optional[int] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
