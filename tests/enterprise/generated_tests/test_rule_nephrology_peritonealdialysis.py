"""
Test Suite for Nephrology - PeritonealDialysis Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_peritonealdialysis import PeritonealDialysisClinicalRuleProcessor


def test_peritonealdialysis_rule_evaluation():
    processor = PeritonealDialysisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_peritonealdialysis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_PERITONEALDIALYSIS"

    res_pass = processor.evaluate({"has_peritonealdialysis": False})
    assert res_pass["passed"] is True
