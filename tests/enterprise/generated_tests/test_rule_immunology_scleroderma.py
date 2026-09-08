"""
Test Suite for Immunology - Scleroderma Rule.
"""

from app.enterprise.generated_rules.rule_immunology_scleroderma import SclerodermaClinicalRuleProcessor


def test_scleroderma_rule_evaluation():
    processor = SclerodermaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_scleroderma": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_SCLERODERMA"

    res_pass = processor.evaluate({"has_scleroderma": False})
    assert res_pass["passed"] is True
