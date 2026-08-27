"""
Test Suite for Infectious - Syphilis Rule.
"""

from app.enterprise.generated_rules.rule_infectious_syphilis import SyphilisClinicalRuleProcessor


def test_syphilis_rule_evaluation():
    processor = SyphilisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_syphilis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_SYPHILIS"

    res_pass = processor.evaluate({"has_syphilis": False})
    assert res_pass["passed"] is True
