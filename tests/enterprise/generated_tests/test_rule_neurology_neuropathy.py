"""
Test Suite for Neurology - Neuropathy Rule.
"""

from app.enterprise.generated_rules.rule_neurology_neuropathy import NeuropathyClinicalRuleProcessor


def test_neuropathy_rule_evaluation():
    processor = NeuropathyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_neuropathy": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_NEUROPATHY"

    res_pass = processor.evaluate({"has_neuropathy": False})
    assert res_pass["passed"] is True
