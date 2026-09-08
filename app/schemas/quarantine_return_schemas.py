"""
Pydantic/Validator Schemas for Quarantine & Return/Recall Workflows (Member 4).
"""

from typing import Optional
from pydantic import BaseModel, Field


class QuarantineCreateSchema(BaseModel):
    bag_id: int = Field(..., description="Target Blood Bag ID")
    reason: str = Field(..., min_length=3, max_length=255, description="Quarantine Trigger Reason")
    suspected_issue: Optional[str] = Field(None, max_length=500, description="Testing pending / Contamination / Quality issue details")
    notes: Optional[str] = Field(None, max_length=500)


class QuarantineResolveSchema(BaseModel):
    resolution: str = Field(..., description="Resolution: RELEASE_TO_AVAILABLE or DISCARD")
    resolution_notes: str = Field(..., min_length=5, max_length=500, description="Authorized Resolution Rationale")


class ReturnRecallCreateSchema(BaseModel):
    bag_id: int = Field(..., description="Target Blood Bag ID")
    return_source: str = Field(..., min_length=2, max_length=150, description="Hospital or Facility Returning Bag")
    reason: str = Field(..., min_length=3, max_length=255, description="Return / Recall Reason")
    inspection_notes: Optional[str] = Field(None, max_length=500, description="Cold chain integrity & seal visual inspection")
    disposition: str = Field("QUARANTINED", description="Immediate disposition: RETURNED_TO_STOCK, QUARANTINED, DISCARDED")
