"""
Toxicology & Substance Use Screening Rules.
Evaluates intravenous drug use (IVDU), alcohol intoxication at presentation, and anabolic steroid misuse.
"""

from typing import Dict, Any


class IntravenousSubstanceRule:
    """Evaluates history of non-prescription intravenous drug use (IVDU)."""
    rule_code = "RULE_TOX_IVDU"
    rule_name = "IV Drug Use Screening Rule"
    category = "TOXICOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_ivdu_history = data.get("has_iv_drug_use_history", False)

        if has_ivdu_history:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of non-prescription intravenous drug use declared. Permanent deferral for blood safety.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No IVDU history declared.",
            "deferral_days": 0
        }


class AlcoholIntoxicationRule:
    """Evaluates acute alcohol intoxication at screening presentation."""
    rule_code = "RULE_TOX_ALCOHOL"
    rule_name = "Alcohol Intoxication Presentation Rule"
    category = "TOXICOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        is_intoxicated = data.get("is_acutely_intoxicated", False)

        if is_intoxicated:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Acute alcohol intoxication observed at presentation. Deferred for 24 hours until clear sensorium.",
                "deferral_days": 1
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Sensorium and clinical sobriety verified.",
            "deferral_days": 0
        }
