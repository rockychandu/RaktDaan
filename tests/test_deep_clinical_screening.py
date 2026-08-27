"""
Exhaustive Automated Unit Test Suite for Deep Clinical Screening & Special Condition Rules.
"""

from app.clinical.rules.deep_screening_rules import (
    AutoimmuneConditionRule, TissueOrganTransplantRule, OncologicalHistoryRule,
    InfectiousDiseaseExposureRule, SpecializedPharmacologyRule
)
from app.clinical.rules.cardiovascular_rules import (
    CardiacArrhythmiaRule, IschemicHeartDiseaseRule, HeartValveProstheticRule
)
from app.clinical.rules.hematology_rules import (
    ThalassemiaTraitRule, BleedingDisorderRule
)
from app.clinical.rules.travel_epidemiology_rules import (
    MalariaTravelRule, ArbovirusTravelRule
)


def test_autoimmune_rule():
    rule = AutoimmuneConditionRule()
    assert rule.evaluate({"has_systemic_lupus": True})["passed"] is False
    assert rule.evaluate({"has_systemic_lupus": False})["passed"] is True


def test_transplant_rule():
    rule = TissueOrganTransplantRule()
    assert rule.evaluate({"has_organ_transplant": True})["passed"] is False
    assert rule.evaluate({"has_organ_transplant": False})["passed"] is True


def test_oncology_rule():
    rule = OncologicalHistoryRule()
    assert rule.evaluate({"has_leukemia_lymphoma": True})["passed"] is False
    assert rule.evaluate({"has_solid_tumor_history": True, "years_in_remission": 2.0})["passed"] is False
    assert rule.evaluate({"has_solid_tumor_history": True, "years_in_remission": 6.0})["passed"] is True


def test_infectious_exposure_rule():
    rule = InfectiousDiseaseExposureRule()
    assert rule.evaluate({"had_needle_stick_injury": True})["passed"] is False
    assert rule.evaluate({"had_needle_stick_injury": False})["passed"] is True


def test_specialized_pharmacology_rule():
    rule = SpecializedPharmacologyRule()
    assert rule.evaluate({"taking_acitretin_neotigason": True})["passed"] is False
    assert rule.evaluate({"taking_acitretin_neotigason": False})["passed"] is True


def test_cardiac_arrhythmia_rule():
    rule = CardiacArrhythmiaRule()
    assert rule.evaluate({"has_cardiac_arrhythmia": True})["passed"] is False
    assert rule.evaluate({"has_cardiac_arrhythmia": False})["passed"] is True


def test_ischemic_heart_disease_rule():
    rule = IschemicHeartDiseaseRule()
    assert rule.evaluate({"has_history_of_myocardial_infarction": True})["passed"] is False
    assert rule.evaluate({"has_history_of_myocardial_infarction": False})["passed"] is True


def test_thalassemia_rule():
    rule = ThalassemiaTraitRule()
    assert rule.evaluate({"has_thalassemia_major": True})["passed"] is False
    assert rule.evaluate({"has_thalassemia_major": False})["passed"] is True


def test_malaria_travel_rule():
    rule = MalariaTravelRule()
    assert rule.evaluate({"had_malaria_infection": True})["passed"] is False
    assert rule.evaluate({"had_malaria_infection": False, "traveled_malaria_endemic_zone": True})["passed"] is False
    assert rule.evaluate({"had_malaria_infection": False, "traveled_malaria_endemic_zone": False})["passed"] is True
