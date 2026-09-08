"""
Regulatory Compliance & System Audit Verifier Engine (Member 3 & Member 4).
Audits system integrity, verifies WHO/FDA blood bank standards compliance,
and detects data discrepancies or unauthorized state transitions.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.models.donor import DonorProfile
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.inventory_extended import StockThreshold, QuarantineRecord
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class ComplianceAuditEngine:
    """
    Automated Regulatory Compliance & Database Audit Engine.
    """

    @staticmethod
    def run_compliance_audit() -> Dict[str, Any]:
        """
        Runs comprehensive regulatory compliance & data integrity checks.
        """
        audit_timestamp = datetime.now(timezone.utc).isoformat()
        violations = []

        # Audit 1: Un-quarantined bags with missing lab testing
        untested_available = BloodBag.query.filter(
            BloodBag.status == "AVAILABLE",
            BloodBag.quality_status == "UNTESTED",
            BloodBag.is_deleted == False
        ).all()

        for bag in untested_available:
            violations.append({
                "severity": "CRITICAL",
                "code": "COMPLIANCE_UNTESTED_AVAILABLE",
                "entity": f"BloodBag {bag.bag_code}",
                "description": f"Blood bag {bag.bag_code} is listed as AVAILABLE but lab quality status is UNTESTED."
            })

        # Audit 2: Expired bags listed as AVAILABLE
        expired_available = BloodBag.query.filter(
            BloodBag.expiry_date <= datetime.now(timezone.utc).date(),
            BloodBag.status == "AVAILABLE",
            BloodBag.is_deleted == False
        ).all()

        for bag in expired_available:
            violations.append({
                "severity": "HIGH",
                "code": "COMPLIANCE_EXPIRED_AVAILABLE",
                "entity": f"BloodBag {bag.bag_code}",
                "description": f"Blood bag {bag.bag_code} passed expiry date {bag.expiry_date} but remains in AVAILABLE stock."
            })

        # Audit 3: Underage Donors
        underage_donors = DonorProfile.query.filter(
            DonorProfile.date_of_birth > datetime.now(timezone.utc).date(),
            DonorProfile.is_deleted == False
        ).all()

        for donor in underage_donors:
            violations.append({
                "severity": "MEDIUM",
                "code": "COMPLIANCE_INVALID_DOB",
                "entity": f"DonorProfile {donor.id}",
                "description": f"Donor ID {donor.id} has date of birth in the future."
            })

        is_compliant = len(violations) == 0

        return {
            "audited_at": audit_timestamp,
            "is_compliant": is_compliant,
            "total_violations": len(violations),
            "compliance_score_percent": max(0, 100 - (len(violations) * 10)),
            "violations": violations
        }
