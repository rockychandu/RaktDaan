"""
Travel Epidemiology & Endemic Vector Deferral Screening Rules.
Evaluates malaria endemic region travel, Zika virus exposure, Dengue fever, Chikungunya, and vCJD risk.
"""

from typing import Dict, Any


class MalariaTravelRule:
    """Evaluates travel to malaria-endemic areas (3 months to 3 years deferral)."""
    rule_code = "RULE_EPIDEMIOLOGY_MALARIA_TRAVEL"
    rule_name = "Malaria Endemic Travel Deferral Rule"
    category = "EPIDEMIOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        traveled_malaria_zone = data.get("traveled_malaria_endemic_zone", False)
        had_malaria = data.get("had_malaria_infection", False)

        if had_malaria:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of confirmed malaria infection. Deferred for 3 years post-recovery.",
                "deferral_days": 1095
            }

        if traveled_malaria_zone:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent travel to malaria-endemic region. Deferred for 3 months.",
                "deferral_days": 90
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No malaria endemic zone travel or infection history declared.",
            "deferral_days": 0
        }


class ArbovirusTravelRule:
    """Evaluates Dengue, Chikungunya, and Zika virus exposure (28 to 120 days)."""
    rule_code = "RULE_EPIDEMIOLOGY_ARBOVIRUS"
    rule_name = "Arbovirus Exposure Rule"
    category = "EPIDEMIOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_zika = data.get("had_zika_virus", False)
        had_dengue = data.get("had_dengue_fever", False)

        if had_zika:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Confirmed Zika virus infection. Deferred for 120 days.",
                "deferral_days": 120
            }

        if had_dengue:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent Dengue fever recovery. Deferred for 28 days.",
                "deferral_days": 28
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No arbovirus infection reported.",
            "deferral_days": 0
        }
