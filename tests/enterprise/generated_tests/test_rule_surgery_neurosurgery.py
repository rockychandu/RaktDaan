"""
Test Suite for Surgery - Neurosurgery Rule.
"""

from app.enterprise.generated_rules.rule_surgery_neurosurgery import NeurosurgeryClinicalRuleProcessor


def test_neurosurgery_rule_evaluation():
    processor = NeurosurgeryClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_neurosurgery": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_NEUROSURGERY"

    res_pass = processor.evaluate({"has_neurosurgery": False})
    assert res_pass["passed"] is True
