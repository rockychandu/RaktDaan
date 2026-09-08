"""
Pediatric & Geriatric Clinical Eligibility Rules.
Evaluates adolescent first-time donor safety, senior donor cardiovascular reserves,
and total blood volume extraction ratio thresholds.
"""

from typing import Dict, Any


class AdolescentDonorSafetyRule:
    """Evaluates 18-21 year old first-time donor safety and total blood volume ratio."""
    rule_code = "RULE_ADV_ADOLESCENT"
    rule_name = "Adolescent First-Time Donor Safety Rule"
    category = "PEDIATRIC_GERIATRIC"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        age = data.get("age", 25)
        weight_kg = data.get("weight_kg", 60.0)
        is_first_time = data.get("is_first_time_donor", False)

        if 18 <= age <= 21 and is_first_time:
            if weight_kg < 55.0:
                return {
                    "passed": False,
                    "rule_code": self.rule_code,
                    "reason": f"Adolescent first-time donor weight ({weight_kg} kg) below safety margin of 55.0 kg (vasovagal reaction prevention).",
                    "deferral_days": 30
                }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Adolescent donor safety volume criteria satisfied.",
            "deferral_days": 0
        }


class SeniorDonorCardiovascularReserveRule:
    """Evaluates senior donors (>65 years) for cardiovascular exercise tolerance."""
    rule_code = "RULE_ADV_SENIOR"
    rule_name = "Senior Donor Reserve Evaluation Rule"
    category = "PEDIATRIC_GERIATRIC"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        age = data.get("age", 30)
        has_physician_clearance = data.get("has_senior_physician_clearance", False)

        if age > 65:
            if not has_physician_clearance:
                return {
                    "passed": False,
                    "rule_code": self.rule_code,
                    "reason": f"Senior donor (age {age} > 65) requires annual physician clearance for cardiovascular reserve safety.",
                    "deferral_days": 365
                }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Senior donor age criteria or physician clearance satisfied.",
            "deferral_days": 0
        }
