"""
Test Suite for Surgery - CardiacBypass Rule.
"""

from app.enterprise.generated_rules.rule_surgery_cardiacbypass import CardiacBypassClinicalRuleProcessor


def test_cardiacbypass_rule_evaluation():
    processor = CardiacBypassClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cardiacbypass": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_CARDIACBYPASS"

    res_pass = processor.evaluate({"has_cardiacbypass": False})
    assert res_pass["passed"] is True
