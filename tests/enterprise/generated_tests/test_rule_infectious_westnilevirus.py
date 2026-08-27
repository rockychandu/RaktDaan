"""
Test Suite for Infectious - WestNileVirus Rule.
"""

from app.enterprise.generated_rules.rule_infectious_westnilevirus import WestNileVirusClinicalRuleProcessor


def test_westnilevirus_rule_evaluation():
    processor = WestNileVirusClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_westnilevirus": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_WESTNILEVIRUS"

    res_pass = processor.evaluate({"has_westnilevirus": False})
    assert res_pass["passed"] is True
