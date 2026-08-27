"""
Extended Cardiology Clinical Rules & Hemodynamic Eligibility Processors.
Covers Cardiomyopathy, Congestive Heart Failure, Pericarditis, Myocarditis, and Coronary Artery Bypass Graft (CABG).
"""

from typing import Dict, Any


class CardiomyopathyRule:
    """Evaluates history of dilated, hypertrophic, or restrictive cardiomyopathy."""
    rule_code = "RULE_CARD_CARDIOMYOPATHY"
    rule_name = "Cardiomyopathy Clinical Rule"
    category = "CARDIOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_cardiomyopathy = data.get("has_cardiomyopathy_diagnosis", False)
        ejection_fraction_pct = data.get("left_ventricular_ejection_fraction_pct", 60.0)

        if has_cardiomyopathy or ejection_fraction_pct < 50.0:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Cardiomyopathy diagnosis or reduced ejection fraction ({ejection_fraction_pct}% < 50%). Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Cardiomyopathy check passed.",
            "deferral_days": 0
        }


class CongestiveHeartFailureRule:
    """Evaluates NYHA Class I-IV Congestive Heart Failure."""
    rule_code = "RULE_CARD_CHF"
    rule_name = "Congestive Heart Failure Rule"
    category = "CARDIOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_chf = data.get("has_congestive_heart_failure", False)
        nyha_class = data.get("nyha_functional_class", 1)

        if has_chf or nyha_class > 1:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Congestive Heart Failure diagnosis or NYHA Functional Class > 1. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No heart failure history declared.",
            "deferral_days": 0
        }


class MyocarditisPericarditisRule:
    """Evaluates acute myocarditis or pericarditis within past 12 months."""
    rule_code = "RULE_CARD_MYOCARDITIS"
    rule_name = "Myocarditis & Pericarditis Rule"
    category = "CARDIOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_myocarditis = data.get("had_recent_myocarditis", False)
        had_pericarditis = data.get("had_recent_pericarditis", False)

        if had_myocarditis or had_pericarditis:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent acute myocarditis or pericarditis diagnosis within 12 months. Deferred for 365 days.",
                "deferral_days": 365
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No inflammatory heart disease reported.",
            "deferral_days": 0
        }
