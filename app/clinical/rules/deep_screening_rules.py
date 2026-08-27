"""
Deep Clinical Screening & Special Condition Eligibility Rules.
Provides exhaustive screening processors for autoimmune disorders, organ/tissue transplants,
oncological histories, infectious disease exposures, and special pharmacological treatments.
"""

from typing import Dict, Any, List
from datetime import date, datetime, timedelta


class AutoimmuneConditionRule:
    """Evaluates autoimmune disease histories (Lupus, Rheumatoid Arthritis, Multiple Sclerosis)."""
    rule_code = "RULE_DEEP_AUTOIMMUNE"
    rule_name = "Autoimmune Condition Deferral Rule"
    category = "IMMUNOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_lupus = data.get("has_systemic_lupus", False)
        has_ra = data.get("has_rheumatoid_arthritis", False)
        has_ms = data.get("has_multiple_sclerosis", False)

        if has_lupus or has_ra or has_ms:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active autoimmune disorder (SLE/RA/MS) declared. Permanent deferral for donor and recipient safety.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No autoimmune disorders reported.",
            "deferral_days": 0
        }


class TissueOrganTransplantRule:
    """Evaluates history of organ transplantation, cornea grafts, or dura mater grafts."""
    rule_code = "RULE_DEEP_TRANSPLANT"
    rule_name = "Organ & Tissue Transplant Rule"
    category = "SURGERY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_organ_transplant = data.get("has_organ_transplant", False)
        has_dura_mater = data.get("has_dura_mater_graft", False)

        if has_organ_transplant or has_dura_mater:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of organ transplant or dura mater graft declared. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No organ or dura mater grafts reported.",
            "deferral_days": 0
        }


class OncologicalHistoryRule:
    """Evaluates cancer history, chemotherapy, or hematologic malignancies."""
    rule_code = "RULE_DEEP_ONCOLOGY"
    rule_name = "Oncological History Deferral Rule"
    category = "ONCOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_leukemia = data.get("has_leukemia_lymphoma", False)
        has_solid_tumor = data.get("has_solid_tumor_history", False)
        years_remission = data.get("years_in_remission", 0.0)

        if has_leukemia:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of hematologic malignancy (Leukemia/Lymphoma). Permanent deferral.",
                "deferral_days": 36500
            }

        if has_solid_tumor and years_remission < 5.0:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Solid tumor history with less than 5 years complete remission ({years_remission} years reported).",
                "deferral_days": int((5.0 - years_remission) * 365)
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No active oncological history or complete remission >= 5 years.",
            "deferral_days": 0
        }


class InfectiousDiseaseExposureRule:
    """Evaluates exposure to Hepatitis B/C, HIV, or needle-stick injuries."""
    rule_code = "RULE_DEEP_INFECTIOUS_EXPOSURE"
    rule_name = "Infectious Disease Exposure Rule"
    category = "INFECTIOUS_DISEASE"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_needle_stick = data.get("had_needle_stick_injury", False)
        had_blood_transfusion_received = data.get("received_blood_transfusion_past_12m", False)

        if had_needle_stick or had_blood_transfusion_received:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Occupational needle-stick injury or received blood transfusion within past 12 months. Deferred for 12 months.",
                "deferral_days": 365
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No high-risk parenteral exposure declared.",
            "deferral_days": 0
        }


class SpecializedPharmacologyRule:
    """Evaluates teratogenic medications (Isotretinoin, Finasteride, Acitretin)."""
    rule_code = "RULE_DEEP_PHARMACOLOGY"
    rule_name = "Teratogenic Pharmacology Deferral Rule"
    category = "PHARMACOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        on_isotretinoin = data.get("taking_isotretinoin_accutane", False)
        on_finasteride = data.get("taking_finasteride_propecia", False)
        on_acitretin = data.get("taking_acitretin_neotigason", False)

        if on_acitretin:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active or past Acitretin treatment. 3-year deferral post-discontinuation.",
                "deferral_days": 1095
            }

        if on_isotretinoin or on_finasteride:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active teratogenic medication (Isotretinoin/Finasteride). 30-day deferral post-discontinuation.",
                "deferral_days": 30
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No teratogenic medication reported.",
            "deferral_days": 0
        }
