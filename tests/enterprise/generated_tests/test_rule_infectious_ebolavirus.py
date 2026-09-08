"""
Test Suite for Infectious - EbolaVirus Rule.
"""

from app.enterprise.generated_rules.rule_infectious_ebolavirus import EbolaVirusClinicalRuleProcessor


def test_ebolavirus_rule_evaluation():
    processor = EbolaVirusClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ebolavirus": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_EBOLAVIRUS"

    res_pass = processor.evaluate({"has_ebolavirus": False})
    assert res_pass["passed"] is True
