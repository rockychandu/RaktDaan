"""
Test Suite for Cardiology - Myocarditis Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_myocarditis import MyocarditisClinicalRuleProcessor


def test_myocarditis_rule_evaluation():
    processor = MyocarditisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_myocarditis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_MYOCARDITIS"

    res_pass = processor.evaluate({"has_myocarditis": False})
    assert res_pass["passed"] is True
