"""
Nephrology & Renal Disease Clinical Eligibility Processors.
Evaluates Chronic Kidney Disease (CKD Stage 1-5), Hemodialysis, Peritoneal Dialysis, and Glomerulonephritis.
"""

from typing import Dict, Any


class ChronicKidneyDiseaseRule:
    """Evaluates CKD Stage 1-5 and eGFR thresholds."""
    rule_code = "RULE_RENAL_CKD"
    rule_name = "Chronic Kidney Disease Rule"
    category = "NEPHROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_ckd = data.get("has_chronic_kidney_disease", False)
        egfr = data.get("estimated_gfr_ml_min", 90.0)

        if has_ckd or egfr < 60.0:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Chronic Kidney Disease diagnosis or reduced eGFR ({egfr} mL/min < 60). Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Renal function criteria satisfied.",
            "deferral_days": 0
        }


class DialysisTherapyRule:
    """Evaluates history of hemodialysis or peritoneal dialysis."""
    rule_code = "RULE_RENAL_DIALYSIS"
    rule_name = "Dialysis Therapy Deferral Rule"
    category = "NEPHROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        on_dialysis = data.get("has_dialysis_history", False)

        if on_dialysis:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of renal dialysis therapy declared. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No dialysis history declared.",
            "deferral_days": 0
        }
