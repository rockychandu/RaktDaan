"""
Test Suite for Surgery - Thyroidectomy Rule.
"""

from app.enterprise.generated_rules.rule_surgery_thyroidectomy import ThyroidectomyClinicalRuleProcessor


def test_thyroidectomy_rule_evaluation():
    processor = ThyroidectomyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_thyroidectomy": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_THYROIDECTOMY"

    res_pass = processor.evaluate({"has_thyroidectomy": False})
    assert res_pass["passed"] is True
