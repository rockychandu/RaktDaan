"""
Test Suite for Infectious - Brucellosis Rule.
"""

from app.enterprise.generated_rules.rule_infectious_brucellosis import BrucellosisClinicalRuleProcessor


def test_brucellosis_rule_evaluation():
    processor = BrucellosisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_brucellosis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_BRUCELLOSIS"

    res_pass = processor.evaluate({"has_brucellosis": False})
    assert res_pass["passed"] is True
