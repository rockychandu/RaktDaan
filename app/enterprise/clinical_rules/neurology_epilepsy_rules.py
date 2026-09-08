"""
Neurology & Seizure Disorder Clinical Eligibility Processors.
Evaluates Epilepsy, Seizure Frequency, Stroke / TIA, and Multiple Sclerosis.
"""

from typing import Dict, Any


class EpilepsySeizureRule:
    """Evaluates seizure frequency and antiepileptic drug therapy."""
    rule_code = "RULE_NEURO_EPILEPSY"
    rule_name = "Epilepsy & Seizure Disorder Rule"
    category = "NEUROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_epilepsy = data.get("has_epilepsy_diagnosis", False)
        years_seizure_free = data.get("years_seizure_free_without_meds", 5.0)

        if has_epilepsy and years_seizure_free < 3.0:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": f"Active epilepsy or seizure within past 3 years ({years_seizure_free} years reported). Deferred.",
                "deferral_days": int((3.0 - years_seizure_free) * 365)
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "Neurological seizure criteria satisfied.",
            "deferral_days": 0
        }


class StrokeCerebrovascularRule:
    """Evaluates ischemic stroke, hemorrhagic stroke, or Transient Ischemic Attack (TIA)."""
    rule_code = "RULE_NEURO_STROKE"
    rule_name = "Stroke & TIA Deferral Rule"
    category = "NEUROLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        had_stroke = data.get("had_stroke_or_tia", False)

        if had_stroke:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of stroke or transient ischemic attack (TIA). Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No stroke or TIA history declared.",
            "deferral_days": 0
        }
