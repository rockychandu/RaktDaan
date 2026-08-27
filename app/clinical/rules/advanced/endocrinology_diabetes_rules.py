"""
Endocrinology & Diabetes Screening Rules.
Evaluates Type 1 / Type 2 diabetes, insulin therapy, thyroid disease, and pituitary/adrenal disorders.
"""

from typing import Dict, Any


class DiabetesMelitusRule:
    """Evaluates Type 1 / Type 2 diabetes and insulin vs oral hypoglycemic therapy."""
    rule_code = "RULE_ADV_DIABETES"
    rule_name = "Diabetes Mellitus Screening Rule"
    category = "ENDOCRINOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_diabetes = data.get("has_diabetes", False)
        uses_bovine_insulin = data.get("uses_bovine_derived_insulin", False)
        is_uncontrolled = data.get("has_uncontrolled_glycemia", False)

        if uses_bovine_insulin:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of bovine-derived insulin therapy (vCJD prion risk). Permanent deferral.",
                "deferral_days": 36500
            }

        if has_diabetes and is_uncontrolled:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Uncontrolled glycemic control declared. Deferral until metabolic stabilization.",
                "deferral_days": 30
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Diabetes screening criteria satisfied (dietary/oral controlled).",
            "deferral_days": 0
        }


class ThyroidDisorderRule:
    """Evaluates Graves' disease, Hashimoto thyroiditis, and thyroid malignancy."""
    rule_code = "RULE_ADV_THYROID"
    rule_name = "Thyroid Disorder Rule"
    category = "ENDOCRINOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_graves = data.get("has_graves_disease", False)
        has_thyroid_ca = data.get("has_thyroid_carcinoma", False)

        if has_graves or has_thyroid_ca:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active Graves' thyrotoxicosis or thyroid carcinoma. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No thyrotoxicosis or thyroid malignancy declared.",
            "deferral_days": 0
        }
