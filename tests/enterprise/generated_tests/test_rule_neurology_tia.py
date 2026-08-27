"""
Test Suite for Neurology - TIA Rule.
"""

from app.enterprise.generated_rules.rule_neurology_tia import TIAClinicalRuleProcessor


def test_tia_rule_evaluation():
    processor = TIAClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_tia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_TIA"

    res_pass = processor.evaluate({"has_tia": False})
    assert res_pass["passed"] is True
