"""
Test Suite for Cardiology - Hypertension Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_hypertension import HypertensionClinicalRuleProcessor


def test_hypertension_rule_evaluation():
    processor = HypertensionClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hypertension": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_HYPERTENSION"

    res_pass = processor.evaluate({"has_hypertension": False})
    assert res_pass["passed"] is True
