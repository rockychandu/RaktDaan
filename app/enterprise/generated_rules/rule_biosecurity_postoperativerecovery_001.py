"""
Enterprise Clinical Screening & Medical Rule Engine: Biosecurity - PostOperativeRecovery (1).
Comprehensive Python decision processor enforcing donor eligibility and transfusion safety standards.
"""

import math
import logging
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


class BiosecurityPostOperativeRecoveryClinicalProcessor1:
    """
    Detailed decision processor evaluating Biosecurity (PostOperativeRecovery) donor pre-screening criteria.
    """
    rule_code = "RULE_ENT_BIOSECURITY_POSTOPERATIVERECOVERY_001"
    rule_name = "Biosecurity PostOperativeRecovery Screening Rule #1"
    category = "BIOSECURITY"
    sub_category = "POSTOPERATIVERECOVERY"

    def __init__(
        self,
        deferral_period_days: int = 180,
        is_permanent_deferral: bool = False,
        requires_physician_clearance: bool = True
    ):
        self.deferral_period_days = deferral_period_days
        self.is_permanent_deferral = is_permanent_deferral
        self.requires_physician_clearance = requires_physician_clearance

    def evaluate_primary_condition(self, donor_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates primary clinical eligibility parameters for Biosecurity (PostOperativeRecovery)."""
        has_primary = donor_payload.get("has_biosecurity_postoperativerecovery_primary", False)
        severity_score = donor_payload.get("biosecurity_postoperativerecovery_severity_score", 0.0)

        if has_primary or severity_score > 3.0:
            def_days = 36500 if self.is_permanent_deferral else self.deferral_period_days
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Primary clinical criteria failed for {self.rule_name} (Severity Score: {severity_score}).",
                "deferral_days": def_days,
                "requires_clearance": self.requires_physician_clearance,
                "category": self.category
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Primary clinical criteria satisfied for {self.rule_name}.",
            "deferral_days": 0,
            "requires_clearance": False,
            "category": self.category
        }

    def evaluate_secondary_indicators(self, donor_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates secondary lab markers, medication interactions, and vital ranges for Biosecurity."""
        lab_marker = donor_payload.get("biosecurity_postoperativerecovery_lab_marker", 10.0)
        is_medicated = donor_payload.get("is_medicated_biosecurity", False)

        if lab_marker < 5.0 or is_medicated:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Secondary laboratory marker or medication criteria failed for {self.rule_name} (Marker: {lab_marker}).",
                "deferral_days": 30,
                "category": self.category
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Secondary indicators verified for {self.rule_name}.",
            "deferral_days": 0,
            "category": self.category
        }

    def compute_next_eligible_date(self, diagnosis_date_str: str) -> Dict[str, Any]:
        """Computes exact next eligible date and countdown for temporary deferrals."""
        try:
            diag_dt = datetime.strptime(diagnosis_date_str[:10], "%Y-%m-%d").date()
            eligible_dt = diag_dt + timedelta(days=self.deferral_period_days)
            today = date.today()
            remaining = (eligible_dt - today).days

            return {
                "diagnosis_date": diagnosis_date_str,
                "next_eligible_date": eligible_dt.isoformat(),
                "days_remaining": max(0, remaining),
                "is_currently_deferred": remaining > 0
            }
        except Exception as e:
            logger.error(f"Error computing return date: {e}")
            return {"error": str(e), "is_currently_deferred": True}

    def generate_audit_summary(self, evaluation_result: Dict[str, Any]) -> str:
        """Generates formatted audit log summary for GAMP5 compliance."""
        status_str = "PASSED" if evaluation_result.get("passed") else "FAILED"
        return f"[AUDIT {self.rule_code}] Result: {status_str} | Reason: {evaluation_result.get('reason')} | Category: {self.category}"
