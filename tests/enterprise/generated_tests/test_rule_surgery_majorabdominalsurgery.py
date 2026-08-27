"""
Test Suite for Surgery - MajorAbdominalSurgery Rule.
"""

from app.enterprise.generated_rules.rule_surgery_majorabdominalsurgery import MajorAbdominalSurgeryClinicalRuleProcessor


def test_majorabdominalsurgery_rule_evaluation():
    processor = MajorAbdominalSurgeryClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_majorabdominalsurgery": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_MAJORABDOMINALSURGERY"

    res_pass = processor.evaluate({"has_majorabdominalsurgery": False})
    assert res_pass["passed"] is True
