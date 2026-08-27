"""
Test Suite for Cardiology - Arrhythmia Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_arrhythmia import ArrhythmiaClinicalRuleProcessor


def test_arrhythmia_rule_evaluation():
    processor = ArrhythmiaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_arrhythmia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_ARRHYTHMIA"

    res_pass = processor.evaluate({"has_arrhythmia": False})
    assert res_pass["passed"] is True
