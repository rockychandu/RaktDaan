"""
Test Suite for Cardiology - Pericarditis Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_pericarditis import PericarditisClinicalRuleProcessor


def test_pericarditis_rule_evaluation():
    processor = PericarditisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_pericarditis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_PERICARDITIS"

    res_pass = processor.evaluate({"has_pericarditis": False})
    assert res_pass["passed"] is True
