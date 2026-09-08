"""
Test Suite for Infectious - ZikaVirus Rule.
"""

from app.enterprise.generated_rules.rule_infectious_zikavirus import ZikaVirusClinicalRuleProcessor


def test_zikavirus_rule_evaluation():
    processor = ZikaVirusClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_zikavirus": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_ZIKAVIRUS"

    res_pass = processor.evaluate({"has_zikavirus": False})
    assert res_pass["passed"] is True
