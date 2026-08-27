"""
Test Suite for Infectious - HepatitisC Rule.
"""

from app.enterprise.generated_rules.rule_infectious_hepatitisc import HepatitisCClinicalRuleProcessor


def test_hepatitisc_rule_evaluation():
    processor = HepatitisCClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hepatitisc": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HEPATITISC"

    res_pass = processor.evaluate({"has_hepatitisc": False})
    assert res_pass["passed"] is True
