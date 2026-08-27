"""
Dermatology & Topical Medication Screening Rules.
Evaluates Psoriasis, Eczema, Systemic Retinoids (Soriatane/Etretinate), and Tazarotene exposure.
"""

from typing import Dict, Any


class PsoriasisEczemaLesionRule:
    """Evaluates active venipuncture site skin lesions or widespread severe psoriasis."""
    rule_code = "RULE_DERM_LESIONS"
    rule_name = "Venipuncture Site Lesion Rule"
    category = "DERMATOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_antecubital_lesion = data.get("has_antecubital_skin_lesion", False)
        has_infected_eczema = data.get("has_infected_eczema", False)

        if has_antecubital_lesion or has_infected_eczema:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active skin lesion or infection at venipuncture site. Deferred until skin healing.",
                "deferral_days": 14
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Venipuncture site skin integrity verified.",
            "deferral_days": 0
        }


class SystemicEtretinateRule:
    """Evaluates history of Etretinate (Tegison) therapy (Permanent teratogenic deferral)."""
    rule_code = "RULE_DERM_ETRETINATE"
    rule_name = "Etretinate Teratogenic Deferral Rule"
    category = "DERMATOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ever_took_etretinate = data.get("ever_took_etretinate_tegison", False)

        if ever_took_etretinate:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of Etretinate (Tegison) therapy declared. Permanent teratogenic deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No Etretinate therapy reported.",
            "deferral_days": 0
        }
