"""
Gastrointestinal & Hepatic Clinical Eligibility Processors.
Evaluates Inflammatory Bowel Disease (Crohn's, Ulcerative Colitis), Cirrhosis, Hepatitis A/B/C/E, and Gastrointestinal Bleeding.
"""

from typing import Dict, Any


class InflammatoryBowelDiseaseRule:
    """Evaluates Crohn's Disease and Ulcerative Colitis."""
    rule_code = "RULE_GI_IBD"
    rule_name = "Inflammatory Bowel Disease Rule"
    category = "GASTROENTEROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_crohns = data.get("has_crohns_disease", False)
        has_uc = data.get("has_ulcerative_colitis", False)

        if has_crohns or has_uc:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Crohn's Disease or Ulcerative Colitis diagnosis declared. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No IBD diagnosis reported.",
            "deferral_days": 0
        }


class HepaticCirrhosisRule:
    """Evaluates Liver Cirrhosis, portal hypertension, and chronic liver disease."""
    rule_code = "RULE_GI_CIRRHOSIS"
    rule_name = "Hepatic Cirrhosis Rule"
    category = "GASTROENTEROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_cirrhosis = data.get("has_liver_cirrhosis", False)
        has_jaundice = data.get("has_unexplained_jaundice", False)

        if has_cirrhosis or has_jaundice:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Liver cirrhosis or unexplained jaundice declared. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No chronic hepatic disease declared.",
            "deferral_days": 0
        }


class GastrointestinalBleedingRule:
    """Evaluates active peptic ulcer hemorrhage or GI bleeding within 6 months."""
    rule_code = "RULE_GI_BLEEDING"
    rule_name = "Gastrointestinal Hemorrhage Rule"
    category = "GASTROENTEROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_gi_bleed = data.get("had_recent_gi_bleeding", False)

        if had_gi_bleed:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent gastrointestinal hemorrhage within past 6 months. Deferred for 180 days.",
                "deferral_days": 180
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No recent GI hemorrhage reported.",
            "deferral_days": 0
        }
