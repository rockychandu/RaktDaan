"""
Pulmonology & Respiratory Clinical Eligibility Rules.
Evaluates severe asthma, COPD, active tuberculosis, and obstructive sleep apnea.
"""

from typing import Dict, Any


class AsthmaSeverityRule:
    """Evaluates acute asthmatic exacerbation vs mild seasonal asthma."""
    rule_code = "RULE_ADV_ASTHMA"
    rule_name = "Pulmonology Asthma Rule"
    category = "PULMONOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_active_wheezing = data.get("has_active_wheezing_today", False)
        on_oral_steroids = data.get("is_on_systemic_corticosteroids", False)

        if has_active_wheezing or on_oral_steroids:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active asthmatic bronchospasm or systemic corticosteroid therapy declared. Deferred for 14 days post-resolution.",
                "deferral_days": 14
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Respiratory pulmonary criteria satisfied.",
            "deferral_days": 0
        }


class TuberculosisRule:
    """Evaluates active pulmonary or extrapulmonary Tuberculosis diagnosis."""
    rule_code = "RULE_ADV_TB"
    rule_name = "Tuberculosis Deferral Rule"
    category = "PULMONOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_active_tb = data.get("has_active_tuberculosis", False)
        years_post_tb_cure = data.get("years_since_tb_completion", 5.0)

        if has_active_tb or years_post_tb_cure < 2.0:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active Tuberculosis or less than 2 years completed post-curative therapy. Deferred.",
                "deferral_days": 730
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No active Tuberculosis infection declared.",
            "deferral_days": 0
        }
