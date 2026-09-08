"""
Test Suite for Infectious - HIV2 Rule.
"""

from app.enterprise.generated_rules.rule_infectious_hiv2 import HIV2ClinicalRuleProcessor


def test_hiv2_rule_evaluation():
    processor = HIV2ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hiv2": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HIV2"

    res_pass = processor.evaluate({"has_hiv2": False})
    assert res_pass["passed"] is True
