"""
Test Suite for Oncology - BreastCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_breastcancer import BreastCancerClinicalRuleProcessor


def test_breastcancer_rule_evaluation():
    processor = BreastCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_breastcancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_BREASTCANCER"

    res_pass = processor.evaluate({"has_breastcancer": False})
    assert res_pass["passed"] is True
