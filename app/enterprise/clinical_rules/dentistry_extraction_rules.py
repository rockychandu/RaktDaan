"""
Dentistry & Maxillofacial Procedure Deferral Screening Rules.
Evaluates routine dental scaling, tooth extraction, root canal, and bone grafting procedures.
"""

from typing import Dict, Any


class DentalExtractionScalingRule:
    """Evaluates minor dental procedures (24h to 7 days transient bacteremia risk)."""
    rule_code = "RULE_DENTAL_PROCEDURE"
    rule_name = "Dental Procedure Bacteremia Rule"
    category = "DENTISTRY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_tooth_extraction = data.get("had_tooth_extraction_past_7d", False)
        had_scaling_clean = data.get("had_scaling_cleaning_past_24h", False)
        had_bone_graft = data.get("had_dental_bone_graft", False)

        if had_bone_graft:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Allogeneic dental bone graft procedure reported. Deferred for 180 days.",
                "deferral_days": 180
            }

        if had_tooth_extraction:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent tooth extraction within 7 days (bacteremia risk). Deferred for 7 days.",
                "deferral_days": 7
            }

        if had_scaling_clean:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent dental scaling/cleaning within 24 hours. Deferred for 24 hours.",
                "deferral_days": 1
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No recent invasive dental procedures reported.",
            "deferral_days": 0
        }
