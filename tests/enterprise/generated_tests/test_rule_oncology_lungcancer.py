"""
Test Suite for Oncology - LungCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_lungcancer import LungCancerClinicalRuleProcessor


def test_lungcancer_rule_evaluation():
    processor = LungCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_lungcancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_LUNGCANCER"

    res_pass = processor.evaluate({"has_lungcancer": False})
    assert res_pass["passed"] is True
