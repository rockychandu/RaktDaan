"""
Medical Screening Questionnaire & Deferral Rules Engine (Member 3).
Defines comprehensive medical questionnaire checklists, medication deferral periods,
permanent contraindication conditions, and travel endemic disease rules according to WHO/NBTC guidelines.
"""

from typing import Dict, Any, List, Optional


class MedicalQuestionnaireCategory:
    GENERAL_HEALTH = "GENERAL_HEALTH"
    MEDICATIONS = "MEDICATIONS"
    TRAVEL_HISTORY = "TRAVEL_HISTORY"
    SURGERY_PROCEDURES = "SURGERY_PROCEDURES"
    HIGH_RISK_BEHAVIOR = "HIGH_RISK_BEHAVIOR"


class DonorMedicalRules:
    """
    Medical Rule Engine for Screening & Deferral Evaluation.
    """

    # Permanent Deferral Conditions (Donor is NEVER eligible to donate)
    PERMANENT_DEFERRAL_CONDITIONS: List[Dict[str, str]] = [
        {"code": "PERM_HIV", "condition": "HIV / AIDS Positive Diagnosis", "category": "INFECTIOUS_DISEASE"},
        {"code": "PERM_HEPB", "condition": "Chronic Hepatitis B Infection", "category": "INFECTIOUS_DISEASE"},
        {"code": "PERM_HEPC", "condition": "Chronic Hepatitis C Infection", "category": "INFECTIOUS_DISEASE"},
        {"code": "PERM_CANCER", "condition": "History of Malignancy / Hematologic Cancer", "category": "ONCOLOGY"},
        {"code": "PERM_CARDIAC", "condition": "Severe Heart Disease / Coronary Bypass", "category": "CARDIOLOGY"},
        {"code": "PERM_INSULIN", "condition": "Insulin-Dependent Diabetes with Vascular Complications", "category": "ENDOCRINOLOGY"},
        {"code": "PERM_AUTOIMMUNE", "condition": "Severe Autoimmune Disorders (Lupus, Rheumatoid Arthritis)", "category": "IMMUNOLOGY"}
    ]

    # Temporary Deferral Medication Periods (Days)
    MEDICATION_DEFERRAL_DAYS: Dict[str, int] = {
        "ANTIBIOTICS": 14,      # Wait 14 days after finishing antibiotics course
        "ASPIRIN": 3,           # Wait 3 days for platelet donation
        "ISOTRETINOIN": 30,     # Accutane / Acne medication (30 days)
        "FINASTERIDE": 30,      # Propecia / Hair loss (30 days)
        "DUTASTERIDE": 180,     # Avodart (6 months)
        "ACITRETIN": 1095,      # Soriatane (3 years)
        "BLOOD_THINNERS": 7     # Anticoagulants (7 days)
    }

    # Temporary Deferral Medical Event Periods (Days)
    EVENT_DEFERRAL_DAYS: Dict[str, int] = {
        "TATTOO_PIERCING": 180,     # 6 Months (180 Days)
        "MAJOR_SURGERY": 180,       # 6 Months
        "MINOR_SURGERY": 30,        # 30 Days
        "DENTAL_EXTRACTION": 7,     # 7 Days
        "PREGNANCY_DELIVERY": 365,  # 1 Year (365 Days) after delivery
        "ABORTION_MISCARRIAGE": 180, # 6 Months
        "MALARIA_TREATMENT": 90,    # 3 Months after complete cure
        "TYPHOID_RECOVERY": 90,     # 3 Months
        "ALCOHOL_CONSUMPTION": 1    # Wait 24 Hours after alcohol consumption
    }

    @classmethod
    def evaluate_medication_deferral(cls, medication_code: str) -> Optional[int]:
        """
        Returns number of deferral days required for a given medication code, or None if no deferral.
        """
        return cls.MEDICATION_DEFERRAL_DAYS.get(medication_code.upper().strip())

    @classmethod
    def evaluate_event_deferral(cls, event_code: str) -> Optional[int]:
        """
        Returns number of deferral days required for a given medical/lifestyle event.
        """
        return cls.EVENT_DEFERRAL_DAYS.get(event_code.upper().strip())

    @classmethod
    def check_permanent_deferral(cls, condition_code: str) -> bool:
        """
        Checks whether a condition code results in permanent deferral.
        """
        codes = [c["code"] for c in cls.PERMANENT_DEFERRAL_CONDITIONS]
        return condition_code.upper().strip() in codes
