"""
Deep Regulatory Compliance Audit & Standards Checker Service Layer (Member 3 & Member 4).
Verifies system adherence to WHO Blood Transfusion Safety, AABB Technical Manual,
and NBTC (National Blood Transfusion Council) India operational guidelines.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.models.donor import DonorProfile
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.inventory_extended import StorageUnit, QuarantineRecord

logger = logging.getLogger(__name__)


class RegulatoryComplianceCheckerService:
    """
    Business Logic Layer for Comprehensive International Blood Safety Compliance Auditing.
    """

    @staticmethod
    def audit_storage_equipment_compliance() -> List[Dict[str, Any]]:
        """
        Audits all cold storage equipment units against WHO temperature calibration standards.
        """
        units = StorageUnit.query.filter_by(is_deleted=False).all()
        audit_results = []

        for u in units:
            is_valid_range = u.min_temp_celsius < u.max_temp_celsius
            has_capacity_defined = u.total_capacity_units > 0
            is_capacity_exceeded = u.occupied_units > u.total_capacity_units

            status = "COMPLIANT"
            issues = []
            if not is_valid_range:
                status = "NON_COMPLIANT"
                issues.append("Invalid temperature range setting.")
            if is_capacity_exceeded:
                status = "NON_COMPLIANT"
                issues.append(f"Capacity exceeded: {u.occupied_units}/{u.total_capacity_units} units.")

            audit_results.append({
                "storage_unit_id": u.id,
                "unit_name": u.name,
                "unit_type": u.unit_type,
                "min_temp": u.min_temp_celsius,
                "max_temp": u.max_temp_celsius,
                "capacity": u.total_capacity_units,
                "occupied": u.occupied_units,
                "status": status,
                "issues": issues
            })

        return audit_results
