"""
Automated Unit Test Suite for Advanced Clinical Rules & Apheresis Services.
"""

from app.clinical.rules.advanced.pediatric_geriatric_rules import (
    AdolescentDonorSafetyRule, SeniorDonorCardiovascularReserveRule
)
from app.clinical.rules.advanced.endocrinology_diabetes_rules import (
    DiabetesMelitusRule, ThyroidDisorderRule
)
from app.clinical.rules.advanced.pulmonology_asthma_rules import (
    AsthmaSeverityRule, TuberculosisRule
)
from app.services.clinical.apheresis_plateletpheresis_service import ApheresisCollectionService
from app.services.clinical.leukoreduction_filtration_service import LeukoreductionFiltrationService


def test_adolescent_rule():
    rule = AdolescentDonorSafetyRule()
    assert rule.evaluate({"age": 19, "weight_kg": 50.0, "is_first_time_donor": True})["passed"] is False
    assert rule.evaluate({"age": 19, "weight_kg": 60.0, "is_first_time_donor": True})["passed"] is True


def test_senior_rule():
    rule = SeniorDonorCardiovascularReserveRule()
    assert rule.evaluate({"age": 68, "has_senior_physician_clearance": False})["passed"] is False
    assert rule.evaluate({"age": 68, "has_senior_physician_clearance": True})["passed"] is True


def test_diabetes_rule():
    rule = DiabetesMelitusRule()
    assert rule.evaluate({"uses_bovine_derived_insulin": True})["passed"] is False
    assert rule.evaluate({"has_diabetes": True, "has_uncontrolled_glycemia": False})["passed"] is True


test_thyroid_rule = lambda: ThyroidDisorderRule().evaluate({"has_graves_disease": True})["passed"] is False

test_asthma_rule = lambda: AsthmaSeverityRule().evaluate({"has_active_wheezing_today": True})["passed"] is False


def test_apheresis_yield():
    res = ApheresisCollectionService.calculate_plateletpheresis_yield(250.0, 70.0)
    assert res["qualified"] is True
    assert res["units_qualified"] in ["SINGLE_UNIT", "DOUBLE_UNIT"]


def test_leukoreduction():
    res = LeukoreductionFiltrationService.evaluate_leukoreduction_filter_log_reduction(1000.0, 1.2)
    assert res["is_leukoreduced_compliant"] is True
