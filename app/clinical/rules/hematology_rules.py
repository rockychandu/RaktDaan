"""
Hematological Clinical Screening Rules.
Evaluates thalassemia, anemia, polycythemia vera, clotting disorders, and hemophilia carrier status.
"""

from typing import Dict, Any


class ThalassemiaTraitRule:
    """Evaluates Thalassemia minor trait vs major status for donor eligibility."""
    rule_code = "RULE_HEMATOLOGY_THALASSEMIA"
    rule_name = "Thalassemia Trait Screening Rule"
    category = "HEMATOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_thalassemia_major = data.get("has_thalassemia_major", False)
        has_thalassemia_minor = data.get("has_thalassemia_minor", False)
        hb = data.get("hemoglobin_level", 13.0)

        if has_thalassemia_major:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Thalassemia Major diagnosis. Permanent donor deferral.",
                "deferral_days": 36500
            }

        if has_thalassemia_minor and hb < 12.5:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Thalassemia Minor trait with low hemoglobin ({hb} g/dL below 12.5 threshold).",
                "deferral_days": 90
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No hemoglobinopathy or Thalassemia Major reported.",
            "deferral_days": 0
        }


class BleedingDisorderRule:
    """Evaluates Hemophilia A/B, Von Willebrand disease, or clotting factor deficiencies."""
    rule_code = "RULE_HEMATOLOGY_BLEEDING_DISORDER"
    rule_name = "Bleeding & Clotting Disorder Rule"
    category = "HEMATOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_hemophilia = data.get("has_hemophilia", False)
        has_vwd = data.get("has_von_willebrand_disease", False)
        has_bleeding_tendency = data.get("has_abnormal_bleeding_tendency", False)

        if has_hemophilia or has_vwd or has_bleeding_tendency:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Bleeding or clotting factor disorder declared. Permanent deferral for donor protection.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No bleeding or coagulation disorders reported.",
            "deferral_days": 0
        }
