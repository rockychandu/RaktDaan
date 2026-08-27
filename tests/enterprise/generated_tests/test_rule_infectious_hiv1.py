"""
Test Suite for Infectious - HIV1 Rule.
"""

from app.enterprise.generated_rules.rule_infectious_hiv1 import HIV1ClinicalRuleProcessor


def test_hiv1_rule_evaluation():
    processor = HIV1ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hiv1": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HIV1"

    res_pass = processor.evaluate({"has_hiv1": False})
    assert res_pass["passed"] is True
