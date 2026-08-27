"""
Pydantic/Validator Schemas for Local Reporting & Export Engine (Member 4).
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ReportFilterSchema(BaseModel):
    report_type: str = Field(..., description="Report category code")
    start_date: Optional[date] = Field(None, description="Start date filter")
    end_date: Optional[date] = Field(None, description="End date filter")
    blood_group: Optional[str] = Field(None, description="Blood group filter")
    component_type: Optional[str] = Field(None, description="Component filter")
    export_format: str = Field("json", description="Export format: json, csv, excel, pdf")
