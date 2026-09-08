"""
Clinical Rule Processor for Toxicology - AnabolicSteroids.
Automated Blood Donor Eligibility & Deferral Evaluation Engine.
"""

from typing import Dict, Any
from datetime import date, datetime, timedelta


class AnabolicSteroidsClinicalRuleProcessor:
    """
    Evaluates donor safety and recipient transmission risk for AnabolicSteroids.
    """
    rule_code = "RULE_TOXICOLOGY_ANABOLICSTEROIDS"
    rule_name = "AnabolicSteroids Screening Rule"
    category = "TOXICOLOGY"

    def __init__(self, deferral_days: int = 180, permanent_deferral: bool = False):
        self.deferral_days = deferral_days
        self.permanent_deferral = permanent_deferral

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_condition = data.get("has_anabolicsteroids", False)
        is_active = data.get("is_anabolicsteroids_active", False)
        years_cured = data.get("years_cured_anabolicsteroids", 0.0)

        if has_condition or is_active:
            def_days = 36500 if self.permanent_deferral else self.deferral_days
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Declared history or active diagnosis of {self.rule_name} ({condition}). Deferred.",
                "deferral_days": def_days,
                "category": self.category
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"No active or historical {condition} condition reported.",
            "deferral_days": 0,
            "category": self.category
        }

    def calculate_recovery_timeline(self, diagnosis_date: str) -> Dict[str, Any]:
        """Calculates recovery date timeline for temporary deferrals."""
        try:
            d_dt = datetime.strptime(diagnosis_date[:10], "%Y-%m-%d").date()
            eligible_dt = d_dt + timedelta(days=self.deferral_days)
            return {
                "diagnosis_date": diagnosis_date,
                "eligible_return_date": eligible_dt.isoformat(),
                "days_remaining": max(0, (eligible_dt - date.today()).days)
            }
        except Exception:
            return {"error": "Invalid date format"}
