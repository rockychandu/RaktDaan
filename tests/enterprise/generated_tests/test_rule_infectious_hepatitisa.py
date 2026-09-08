"""
Test Suite for Infectious - HepatitisA Rule.
"""

from app.enterprise.generated_rules.rule_infectious_hepatitisa import HepatitisAClinicalRuleProcessor


def test_hepatitisa_rule_evaluation():
    processor = HepatitisAClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hepatitisa": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HEPATITISA"

    res_pass = processor.evaluate({"has_hepatitisa": False})
    assert res_pass["passed"] is True
