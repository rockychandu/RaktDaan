"""
Test Suite for Cardiology - AorticAneurysm Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_aorticaneurysm import AorticAneurysmClinicalRuleProcessor


def test_aorticaneurysm_rule_evaluation():
    processor = AorticAneurysmClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_aorticaneurysm": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_AORTICANEURYSM"

    res_pass = processor.evaluate({"has_aorticaneurysm": False})
    assert res_pass["passed"] is True
