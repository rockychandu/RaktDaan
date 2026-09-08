"""
Test Suite for Infectious - Chikungunya Rule.
"""

from app.enterprise.generated_rules.rule_infectious_chikungunya import ChikungunyaClinicalRuleProcessor


def test_chikungunya_rule_evaluation():
    processor = ChikungunyaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_chikungunya": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_CHIKUNGUNYA"

    res_pass = processor.evaluate({"has_chikungunya": False})
    assert res_pass["passed"] is True
