"""
Clinical Vitals Eligibility Rules for Blood Donor Pre-Screening.
Includes Age, Weight, Hemoglobin, Blood Pressure, Pulse, and Temperature Rule Processors.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta


class BaseClinicalRule:
    """Base class for all clinical screening rules."""
    rule_code: str = "BASE_RULE"
    rule_name: str = "Base Clinical Rule"
    category: str = "GENERAL"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement evaluate()")


class AgeEligibilityRule(BaseClinicalRule):
    """
    Evaluates donor age against standard blood bank eligibility bounds (18 to 65 years).
    """
    rule_code = "RULE_VITAL_AGE"
    rule_name = "Donor Age Requirement Rule"
    category = "VITALS"

    def __init__(self, min_age: int = 18, max_age: int = 65):
        self.min_age = min_age
        self.max_age = max_age

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        dob = data.get("date_of_birth")
        age = data.get("age")

        if age is None and dob is not None:
            if isinstance(dob, str):
                dob_dt = datetime.strptime(dob[:10], "%Y-%m-%d").date()
            elif isinstance(dob, (date, datetime)):
                dob_dt = dob if isinstance(dob, date) else dob.date()
            else:
                dob_dt = date.today()
            today = date.today()
            age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))

        if age is None:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Donor age or date of birth not provided.",
                "deferral_days": 0
            }

        if age < self.min_age:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Donor age ({age} years) is below minimum required age of {self.min_age} years.",
                "deferral_days": int((self.min_age - age) * 365)
            }

        if age > self.max_age:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Donor age ({age} years) exceeds maximum allowed age of {self.max_age} years.",
                "deferral_days": 3650
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Age {age} years is within eligible range ({self.min_age}-{self.max_age} years).",
            "deferral_days": 0
        }


class WeightEligibilityRule(BaseClinicalRule):
    """
    Evaluates donor body weight against minimum safety threshold (50.0 kg for 350ml/450ml donation).
    """
    rule_code = "RULE_VITAL_WEIGHT"
    rule_name = "Body Weight Threshold Rule"
    category = "VITALS"

    def __init__(self, min_weight_kg: float = 50.0):
        self.min_weight_kg = min_weight_kg

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        weight = data.get("weight_kg")
        if weight is None:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Body weight measurement not provided.",
                "deferral_days": 0
            }

        if weight < self.min_weight_kg:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Body weight ({weight} kg) is below minimum threshold of {self.min_weight_kg} kg.",
                "deferral_days": 30
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Body weight {weight} kg satisfies minimum requirement of {self.min_weight_kg} kg.",
            "deferral_days": 0
        }


class HemoglobinEligibilityRule(BaseClinicalRule):
    """
    Evaluates hemoglobin levels against male/female standards (Minimum 12.5 g/dL).
    """
    rule_code = "RULE_VITAL_HEMOGLOBIN"
    rule_name = "Hemoglobin Concentration Rule"
    category = "VITALS"

    def __init__(self, min_hb_g_dl: float = 12.5, max_hb_g_dl: float = 18.0):
        self.min_hb = min_hb_g_dl
        self.max_hb = max_hb_g_dl

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hb = data.get("hemoglobin_level")
        if hb is None:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Hemoglobin reading not provided.",
                "deferral_days": 0
            }

        if hb < self.min_hb:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Hemoglobin level ({hb} g/dL) is below minimum threshold of {self.min_hb} g/dL.",
                "deferral_days": 30
            }

        if hb > self.max_hb:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Hemoglobin level ({hb} g/dL) exceeds maximum physiological threshold of {self.max_hb} g/dL (polycythemia risk).",
                "deferral_days": 60
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Hemoglobin level {hb} g/dL is within acceptable range ({self.min_hb}-{self.max_hb} g/dL).",
            "deferral_days": 0
        }


class BloodPressureEligibilityRule(BaseClinicalRule):
    """
    Evaluates Systolic and Diastolic Blood Pressure against safe limits (Sys: 90-140 mmHg, Dia: 60-90 mmHg).
    """
    rule_code = "RULE_VITAL_BP"
    rule_name = "Blood Pressure Hemodynamics Rule"
    category = "VITALS"

    def __init__(self, min_sys=90, max_sys=140, min_dia=60, max_dia=90):
        self.min_sys = min_sys
        self.max_sys = max_sys
        self.min_dia = min_dia
        self.max_dia = max_dia

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sys_bp = data.get("blood_pressure_sys")
        dia_bp = data.get("blood_pressure_dia")

        if sys_bp is None or dia_bp is None:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Complete Blood Pressure readings (Systolic & Diastolic) not provided.",
                "deferral_days": 0
            }

        reasons = []
        if sys_bp < self.min_sys or sys_bp > self.max_sys:
            reasons.append(f"Systolic BP ({sys_bp} mmHg) outside range ({self.min_sys}-{self.max_sys} mmHg)")

        if dia_bp < self.min_dia or dia_bp > self.max_dia:
            reasons.append(f"Diastolic BP ({dia_bp} mmHg) outside range ({self.min_dia}-{self.max_dia} mmHg)")

        if len(reasons) > 0:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Blood Pressure check failed: {'; '.join(reasons)}.",
                "deferral_days": 14
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Blood Pressure {sys_bp}/{dia_bp} mmHg is within normal limits.",
            "deferral_days": 0
        }


class PulseRateEligibilityRule(BaseClinicalRule):
    """
    Evaluates resting pulse rate (60 to 100 bpm).
    """
    rule_code = "RULE_VITAL_PULSE"
    rule_name = "Resting Pulse Rate Rule"
    category = "VITALS"

    def __init__(self, min_pulse=60, max_pulse=100):
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pulse = data.get("pulse_rate")
        if pulse is None:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Pulse rate measurement not provided.",
                "deferral_days": 0
            }

        if pulse < self.min_pulse or pulse > self.max_pulse:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Pulse rate ({pulse} bpm) outside acceptable resting range ({self.min_pulse}-{self.max_pulse} bpm).",
                "deferral_days": 7
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Pulse rate {pulse} bpm is normal.",
            "deferral_days": 0
        }


class TemperatureEligibilityRule(BaseClinicalRule):
    """
    Evaluates body temperature (<= 37.5 °C).
    """
    rule_code = "RULE_VITAL_TEMP"
    rule_name = "Body Temperature Rule"
    category = "VITALS"

    def __init__(self, max_temp_celsius: float = 37.5):
        self.max_temp = max_temp_celsius

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        temp = data.get("temp_celsius")
        if temp is None:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Body temperature measurement not provided.",
                "deferral_days": 0
            }

        if temp > self.max_temp:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Body temperature ({temp}°C) exceeds pyrexia limit of {self.max_temp}°C.",
                "deferral_days": 14
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Body temperature {temp}°C is normal.",
            "deferral_days": 0
        }
