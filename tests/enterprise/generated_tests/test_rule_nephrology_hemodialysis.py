"""
Test Suite for Nephrology - Hemodialysis Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_hemodialysis import HemodialysisClinicalRuleProcessor


def test_hemodialysis_rule_evaluation():
    processor = HemodialysisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hemodialysis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_HEMODIALYSIS"

    res_pass = processor.evaluate({"has_hemodialysis": False})
    assert res_pass["passed"] is True
