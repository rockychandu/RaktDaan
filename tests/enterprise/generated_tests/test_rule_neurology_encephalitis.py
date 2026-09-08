"""
Test Suite for Neurology - Encephalitis Rule.
"""

from app.enterprise.generated_rules.rule_neurology_encephalitis import EncephalitisClinicalRuleProcessor


def test_encephalitis_rule_evaluation():
    processor = EncephalitisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_encephalitis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_ENCEPHALITIS"

    res_pass = processor.evaluate({"has_encephalitis": False})
    assert res_pass["passed"] is True
