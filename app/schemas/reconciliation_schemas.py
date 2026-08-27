"""
Pydantic/Validator Schemas for Physical Stock Reconciliation (Member 4).
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from app.users.models import BloodGroup


class StockReconciliationItemSchema(BaseModel):
    blood_group: str = Field(..., description="Human Blood Group")
    component_type: str = Field(..., description="Component Type")
    physical_count: int = Field(..., ge=0, description="Actual Physical Counted Units")
    notes: Optional[str] = Field(None, max_length=255)


class StockReconciliationSubmitSchema(BaseModel):
    items: List[StockReconciliationItemSchema] = Field(..., min_items=1, max_items=50)
    audit_reason: str = Field(..., min_length=5, max_length=255, description="Reason for physical audit reconciliation")
