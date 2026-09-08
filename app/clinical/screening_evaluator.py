"""
Master Clinical Screening Evaluator Engine.
Orchestrates all configurable vital and medical history rules to produce a final PASS/FAIL decision,
detailed failure reasons, and calculated next eligible review date.
"""

from typing import Dict, Any, List
from datetime import date, timedelta

from app.clinical.rules.vitals_rules import (
    AgeEligibilityRule, WeightEligibilityRule, HemoglobinEligibilityRule,
    BloodPressureEligibilityRule, PulseRateEligibilityRule, TemperatureEligibilityRule
)
from app.clinical.rules.medical_history_rules import (
    InfectionStatusRule, HospitalizationRule, SurgeryProcedureRule,
    MedicationDeclarationRule, VaccinationRule, PregnancyRule, DonationIntervalRule
)


class MasterClinicalScreeningEvaluator:
    """
    Enterprise Clinical Screening Engine that executes all configured pre-screening rules.
    """

    def __init__(self):
        self.rules = [
            AgeEligibilityRule(),
            WeightEligibilityRule(),
            HemoglobinEligibilityRule(),
            BloodPressureEligibilityRule(),
            PulseRateEligibilityRule(),
            TemperatureEligibilityRule(),
            InfectionStatusRule(),
            HospitalizationRule(),
            SurgeryProcedureRule(),
            MedicationDeclarationRule(),
            VaccinationRule(),
            PregnancyRule(),
            DonationIntervalRule()
        ]

    def evaluate_donor_checkup(self, donor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes all clinical rules against donor checkup input.
        Returns a comprehensive evaluation report.
        """
        rule_results: List[Dict[str, Any]] = []
        failed_reasons: List[str] = []
        passed_rules: List[str] = []
        max_deferral_days = 0

        for rule in self.rules:
            res = rule.evaluate(donor_data)
            rule_results.append(res)

            if not res["passed"]:
                failed_reasons.append(res["reason"])
                if res.get("deferral_days", 0) > max_deferral_days:
                    max_deferral_days = res["deferral_days"]
            else:
                passed_rules.append(res["rule_code"])

        overall_passed = len(failed_reasons) == 0
        screening_date = date.today().isoformat()
        next_eligible_date = (date.today() + timedelta(days=max_deferral_days)).isoformat() if max_deferral_days > 0 else screening_date

        return {
            "is_passed": overall_passed,
            "screening_status": "PASSED" if overall_passed else "FAILED",
            "eligibility_status": "ELIGIBLE" if overall_passed else "TEMPORARILY_DEFERRED",
            "summary_message": "Health checkup passed. You can proceed to the donation process." if overall_passed else "Sorry, you cannot donate blood at this time.",
            "screening_date": screening_date,
            "next_eligible_date": next_eligible_date,
            "max_deferral_days": max_deferral_days,
            "reasons": failed_reasons,
            "rule_details": rule_results,
            "passed_rules_count": len(passed_rules),
            "failed_rules_count": len(failed_reasons)
        }
