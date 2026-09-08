"""
Test Suite for Cardiology - Pacemaker Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_pacemaker import PacemakerClinicalRuleProcessor


def test_pacemaker_rule_evaluation():
    processor = PacemakerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_pacemaker": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_PACEMAKER"

    res_pass = processor.evaluate({"has_pacemaker": False})
    assert res_pass["passed"] is True
