"""
Test Suite for Neurology - Stroke Rule.
"""

from app.enterprise.generated_rules.rule_neurology_stroke import StrokeClinicalRuleProcessor


def test_stroke_rule_evaluation():
    processor = StrokeClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_stroke": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_STROKE"

    res_pass = processor.evaluate({"has_stroke": False})
    assert res_pass["passed"] is True
