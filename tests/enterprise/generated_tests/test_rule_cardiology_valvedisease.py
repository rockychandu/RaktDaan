"""
Test Suite for Cardiology - ValveDisease Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_valvedisease import ValveDiseaseClinicalRuleProcessor


def test_valvedisease_rule_evaluation():
    processor = ValveDiseaseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_valvedisease": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_VALVEDISEASE"

    res_pass = processor.evaluate({"has_valvedisease": False})
    assert res_pass["passed"] is True
