"""
Automated Test Suite for Clinical Screening Rules & Eligibility Engine.
"""

from app.clinical.screening_evaluator import MasterClinicalScreeningEvaluator
from app.clinical.rules.vitals_rules import (
    AgeEligibilityRule, WeightEligibilityRule, HemoglobinEligibilityRule,
    BloodPressureEligibilityRule, PulseRateEligibilityRule, TemperatureEligibilityRule
)
from app.clinical.rules.medical_history_rules import (
    InfectionStatusRule, HospitalizationRule, SurgeryProcedureRule,
    MedicationDeclarationRule, VaccinationRule, PregnancyRule, DonationIntervalRule
)


def test_age_rule():
    rule = AgeEligibilityRule()
    assert rule.evaluate({"age": 25})["passed"] is True
    assert rule.evaluate({"age": 16})["passed"] is False
    assert rule.evaluate({"age": 70})["passed"] is False


def test_weight_rule():
    rule = WeightEligibilityRule()
    assert rule.evaluate({"weight_kg": 60.0})["passed"] is True
    assert rule.evaluate({"weight_kg": 45.0})["passed"] is False


def test_hemoglobin_rule():
    rule = HemoglobinEligibilityRule()
    assert rule.evaluate({"hemoglobin_level": 14.0})["passed"] is True
    assert rule.evaluate({"hemoglobin_level": 10.5})["passed"] is False
    assert rule.evaluate({"hemoglobin_level": 20.0})["passed"] is False


def test_blood_pressure_rule():
    rule = BloodPressureEligibilityRule()
    assert rule.evaluate({"blood_pressure_sys": 120, "blood_pressure_dia": 80})["passed"] is True
    assert rule.evaluate({"blood_pressure_sys": 160, "blood_pressure_dia": 100})["passed"] is False


def test_pulse_rule():
    rule = PulseRateEligibilityRule()
    assert rule.evaluate({"pulse_rate": 72})["passed"] is True
    assert rule.evaluate({"pulse_rate": 120})["passed"] is False


def test_temperature_rule():
    rule = TemperatureEligibilityRule()
    assert rule.evaluate({"temp_celsius": 36.6})["passed"] is True
    assert rule.evaluate({"temp_celsius": 38.5})["passed"] is False


def test_infection_rule():
    rule = InfectionStatusRule()
    assert rule.evaluate({"has_recent_infection": False, "has_chronic_illness": False})["passed"] is True
    assert rule.evaluate({"has_recent_infection": True})["passed"] is False


def test_pregnancy_rule():
    rule = PregnancyRule()
    assert rule.evaluate({"gender": "FEMALE", "is_currently_pregnant": False})["passed"] is True
    assert rule.evaluate({"gender": "FEMALE", "is_currently_pregnant": True})["passed"] is False
    assert rule.evaluate({"gender": "MALE", "is_currently_pregnant": True})["passed"] is True


def test_master_screening_evaluator_pass():
    evaluator = MasterClinicalScreeningEvaluator()
    res = evaluator.evaluate_donor_checkup({
        "age": 30,
        "weight_kg": 65.0,
        "hemoglobin_level": 14.0,
        "blood_pressure_sys": 120,
        "blood_pressure_dia": 80,
        "pulse_rate": 72,
        "temp_celsius": 36.6,
        "has_chronic_illness": False,
        "is_on_medication": False,
        "gender": "MALE"
    })
    assert res["is_passed"] is True
    assert res["screening_status"] == "PASSED"
    assert res["eligibility_status"] == "ELIGIBLE"


def test_master_screening_evaluator_fail():
    evaluator = MasterClinicalScreeningEvaluator()
    res = evaluator.evaluate_donor_checkup({
        "age": 30,
        "weight_kg": 42.0, # Failed
        "hemoglobin_level": 10.0, # Failed
        "blood_pressure_sys": 160, # Failed
        "blood_pressure_dia": 100,
        "pulse_rate": 120, # Failed
        "temp_celsius": 38.5, # Failed
        "has_chronic_illness": True, # Failed
        "is_on_medication": False,
        "gender": "MALE"
    })
    assert res["is_passed"] is False
    assert res["screening_status"] == "FAILED"
    assert res["eligibility_status"] == "TEMPORARILY_DEFERRED"
    assert len(res["reasons"]) >= 5
