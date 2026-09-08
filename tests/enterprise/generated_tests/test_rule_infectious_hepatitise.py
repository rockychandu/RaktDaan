"""
Test Suite for Infectious - HepatitisE Rule.
"""

from app.enterprise.generated_rules.rule_infectious_hepatitise import HepatitisEClinicalRuleProcessor


def test_hepatitise_rule_evaluation():
    processor = HepatitisEClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hepatitise": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HEPATITISE"

    res_pass = processor.evaluate({"has_hepatitise": False})
    assert res_pass["passed"] is True
