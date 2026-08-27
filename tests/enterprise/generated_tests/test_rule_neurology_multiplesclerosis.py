"""
Test Suite for Neurology - MultipleSclerosis Rule.
"""

from app.enterprise.generated_rules.rule_neurology_multiplesclerosis import MultipleSclerosisClinicalRuleProcessor


def test_multiplesclerosis_rule_evaluation():
    processor = MultipleSclerosisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_multiplesclerosis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_MULTIPLESCLEROSIS"

    res_pass = processor.evaluate({"has_multiplesclerosis": False})
    assert res_pass["passed"] is True
