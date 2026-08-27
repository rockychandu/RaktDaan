"""
Test Suite for Infectious - HepatitisB Rule.
"""

from app.enterprise.generated_rules.rule_infectious_hepatitisb import HepatitisBClinicalRuleProcessor


def test_hepatitisb_rule_evaluation():
    processor = HepatitisBClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hepatitisb": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HEPATITISB"

    res_pass = processor.evaluate({"has_hepatitisb": False})
    assert res_pass["passed"] is True
