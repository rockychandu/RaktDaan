"""
Test Suite for Cardiology - HeartFailure Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_heartfailure import HeartFailureClinicalRuleProcessor


def test_heartfailure_rule_evaluation():
    processor = HeartFailureClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_heartfailure": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_HEARTFAILURE"

    res_pass = processor.evaluate({"has_heartfailure": False})
    assert res_pass["passed"] is True
