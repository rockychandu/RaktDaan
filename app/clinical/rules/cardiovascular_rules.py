"""
Cardiovascular Clinical Eligibility Rules for Blood Donor Screening.
Evaluates arrhythmia, hypertension staging, ischemic heart disease, valve replacements, and pacemaker declarations.
"""

from typing import Dict, Any


class CardiacArrhythmiaRule:
    """Evaluates cardiac arrhythmia declarations and resting pulse regularity."""
    rule_code = "RULE_CARDIO_ARRHYTHMIA"
    rule_name = "Cardiac Arrhythmia Screening Rule"
    category = "CARDIOVASCULAR"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_arrhythmia = data.get("has_cardiac_arrhythmia", False)
        pulse = data.get("pulse_rate", 72)
        is_irregular = data.get("is_pulse_irregular", False)

        if has_arrhythmia or is_irregular:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Declared cardiac arrhythmia or irregular resting pulse detected.",
                "deferral_days": 365
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Pulse rhythm is regular with no declared arrhythmia history.",
            "deferral_days": 0
        }


class IschemicHeartDiseaseRule:
    """Evaluates history of myocardial infarction, angina pectoris, or coronary angioplasty."""
    rule_code = "RULE_CARDIO_ISCHEMIC"
    rule_name = "Ischemic Heart Disease Rule"
    category = "CARDIOVASCULAR"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_mi = data.get("has_history_of_myocardial_infarction", False)
        has_angina = data.get("has_angina_pectoris", False)
        has_stent = data.get("has_coronary_stent", False)

        if has_mi or has_angina or has_stent:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of ischemic heart disease, myocardial infarction, or coronary angioplasty. Permanent deferral for donor safety.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No history of ischemic heart disease reported.",
            "deferral_days": 0
        }


class HeartValveProstheticRule:
    """Evaluates prosthetic valve replacement or active anticoagulant therapy."""
    rule_code = "RULE_CARDIO_VALVE"
    rule_name = "Heart Valve Replacement Rule"
    category = "CARDIOVASCULAR"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_prosthetic_valve = data.get("has_prosthetic_heart_valve", False)
        on_anticoagulants = data.get("is_on_anticoagulants", False)

        if has_prosthetic_valve or on_anticoagulants:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Prosthetic valve replacement or active anticoagulant therapy. Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No prosthetic valve replacement declared.",
            "deferral_days": 0
        }
