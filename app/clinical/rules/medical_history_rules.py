"""
Clinical Medical History & Infection Deferral Screening Rules.
Evaluates chronic conditions, recent infections, hospitalization, surgeries, vaccinations, medications, and pregnancy.
"""

from typing import Dict, Any
from datetime import date, datetime, timedelta


class InfectionStatusRule:
    """Evaluates recent viral or bacterial infection declarations."""
    rule_code = "RULE_MED_INFECTION"
    rule_name = "Recent Infection Deferral Rule"
    category = "MEDICAL_HISTORY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_infection = data.get("has_recent_infection", False)
        fever = data.get("has_chronic_illness", False)

        if has_infection or fever:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Active or recent infection/fever reported within the past 14 days.",
                "deferral_days": 14
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No recent active infection reported.",
            "deferral_days": 0
        }


class HospitalizationRule:
    """Evaluates recent hospitalization declarations within last 6 months."""
    rule_code = "RULE_MED_HOSPITALIZATION"
    rule_name = "Recent Hospitalization Deferral Rule"
    category = "MEDICAL_HISTORY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hospitalized = data.get("has_recent_hospitalization", False)

        if hospitalized:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent major hospitalization reported within the past 6 months.",
                "deferral_days": 180
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No recent hospitalization reported.",
            "deferral_days": 0
        }


class SurgeryProcedureRule:
    """Evaluates recent surgical procedures (minor: 3 months, major: 6-12 months)."""
    rule_code = "RULE_MED_SURGERY"
    rule_name = "Surgical Procedure Deferral Rule"
    category = "SURGERY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_surgery = data.get("has_recent_surgery", False)
        surgery_type = data.get("surgery_type", "NONE")

        if had_surgery:
            deferral = 180 if surgery_type == "MAJOR" else 90
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Recent {surgery_type.lower()} surgical procedure reported.",
                "deferral_days": deferral
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No recent surgical procedures declared.",
            "deferral_days": 0
        }


class MedicationDeclarationRule:
    """Evaluates prescription medications (antibiotics: 14 days, blood thinners/retinoids: 30-180 days)."""
    rule_code = "RULE_MED_MEDICATION"
    rule_name = "Medication Deferral Rule"
    category = "MEDICATIONS"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        is_on_meds = data.get("is_on_medication", False)
        med_category = data.get("medication_category", "GENERAL")

        if is_on_meds:
            deferral = 30 if med_category in ["ANTIBIOTICS", "BLOOD_PRESSURE"] else 14
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Active medication declared under category '{med_category}'.",
                "deferral_days": deferral
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No deferred prescription medications reported.",
            "deferral_days": 0
        }


class VaccinationRule:
    """Evaluates recent vaccination declarations (live-attenuated: 28 days, inactivated: 14 days)."""
    rule_code = "RULE_MED_VACCINATION"
    rule_name = "Vaccination Deferral Rule"
    category = "VACCINATION"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        vaccinated = data.get("has_recent_vaccination", False)
        vac_type = data.get("vaccine_type", "INACTIVATED")

        if vaccinated:
            deferral = 28 if vac_type == "LIVE_ATTENUATED" else 14
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Recent vaccination ({vac_type}) reported within deferral window.",
                "deferral_days": deferral
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No recent deferred vaccinations reported.",
            "deferral_days": 0
        }


class PregnancyRule:
    """Evaluates pregnancy, lactation, and recent childbirth eligibility for female donors."""
    rule_code = "RULE_MED_PREGNANCY"
    rule_name = "Pregnancy & Lactation Deferral Rule"
    category = "PREGNANCY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        gender = str(data.get("gender", "")).upper()
        if gender != "FEMALE":
            return {
                "passed": True,
                "rule_code": self.rule_code,
                "reason": "Pregnancy rule non-applicable for non-female donors.",
                "deferral_days": 0
            }

        is_pregnant = data.get("is_currently_pregnant", False)
        is_breastfeeding = data.get("is_breastfeeding", False)
        recent_delivery = data.get("recent_delivery_within_12_months", False)

        if is_pregnant:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Currently pregnant. Donation deferred throughout pregnancy.",
                "deferral_days": 365
            }

        if is_breastfeeding or recent_delivery:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "Recent childbirth or active lactation declared. Deferred for 12 months post-delivery.",
                "deferral_days": 365
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No pregnancy or recent delivery deferral.",
            "deferral_days": 0
        }


class DonationIntervalRule:
    """Evaluates minimum interval since last donation (Males: 90 days, Females: 120 days)."""
    rule_code = "RULE_MED_DONATION_INTERVAL"
    rule_name = "Donation Frequency Interval Rule"
    category = "INTERVAL"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        last_date = data.get("last_donation_date")
        gender = str(data.get("gender", "")).upper()

        if not last_date:
            return {
                "passed": True,
                "rule_code": self.rule_code,
                "reason": "First-time donor or no previous donation recorded.",
                "deferral_days": 0
            }

        if isinstance(last_date, str):
            last_date_dt = datetime.strptime(last_date[:10], "%Y-%m-%d").date()
        elif isinstance(last_date, (date, datetime)):
            last_date_dt = last_date if isinstance(last_date, date) else last_date.date()
        else:
            return {"passed": True, "rule_code": self.rule_code, "reason": "Valid last donation date", "deferral_days": 0}

        required_interval_days = 120 if gender == "FEMALE" else 90
        days_since = (date.today() - last_date_dt).days

        if days_since < required_interval_days:
            remaining = required_interval_days - days_since
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Minimum interval since last donation not met ({days_since} days elapsed, required: {required_interval_days} days).",
                "deferral_days": remaining
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": f"Interval of {days_since} days since last donation satisfies requirement.",
            "deferral_days": 0
        }
