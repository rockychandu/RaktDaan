"""
Test Suite for Neurology - Parkinsons Rule.
"""

from app.enterprise.generated_rules.rule_neurology_parkinsons import ParkinsonsClinicalRuleProcessor


def test_parkinsons_rule_evaluation():
    processor = ParkinsonsClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_parkinsons": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_PARKINSONS"

    res_pass = processor.evaluate({"has_parkinsons": False})
    assert res_pass["passed"] is True
