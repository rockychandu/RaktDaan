"""
Test Suite for Surgery - Splenectomy Rule.
"""

from app.enterprise.generated_rules.rule_surgery_splenectomy import SplenectomyClinicalRuleProcessor


def test_splenectomy_rule_evaluation():
    processor = SplenectomyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_splenectomy": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_SPLENECTOMY"

    res_pass = processor.evaluate({"has_splenectomy": False})
    assert res_pass["passed"] is True
