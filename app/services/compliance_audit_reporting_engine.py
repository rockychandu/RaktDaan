"""
Regulatory Compliance & Quality System Audit Engine.
Enforces WHO / FDA blood bank standards, equipment calibration tracking,
cold chain SLA audits, and regulatory export reports.
"""

import logging
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, List
from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.inventory_extended import StorageUnit, QuarantineRecord
from app.database.models.serology import SerologyTestRecord

logger = logging.getLogger(__name__)


class ComplianceAuditReportingEngine:
    """
    Quality Management System Audit Service.
    """

    @staticmethod
    def audit_cold_chain_sla_compliance() -> Dict[str, Any]:
        """
        Audits storage units for temperature compliance (Whole blood: 2°C - 6°C).
        """
        units = StorageUnit.query.all()
        compliant_units = []
        violations = []

        for u in units:
            temp = u.current_temperature_celsius
            if temp is not None:
                if u.min_temp_threshold <= temp <= u.max_temp_threshold:
                    compliant_units.append(u.unit_code)
                else:
                    violations.append({
                        "unit_code": u.unit_code,
                        "current_temp": temp,
                        "allowed_range": f"{u.min_temp_threshold}°C - {u.max_temp_threshold}°C"
                    })

        is_compliant = len(violations) == 0
        return {
            "is_audit_compliant": is_compliant,
            "total_storage_units": len(units),
            "compliant_units_count": len(compliant_units),
            "violations_count": len(violations),
            "violations": violations,
            "audit_timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def audit_untested_blood_bags() -> Dict[str, Any]:
        """
        Audits blood bags for missing serology screening panels.
        """
        all_bags = BloodBag.query.filter_by(is_deleted=False).all()
        untested = []

        for bag in all_bags:
            if not bag.serology_records and bag.status == "AVAILABLE":
                untested.append(bag.bag_code)

        return {
            "untested_bags_in_available_stock": len(untested),
            "untested_bag_codes": untested,
            "is_compliant": len(untested) == 0
        }
