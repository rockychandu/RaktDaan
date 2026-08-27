"""
Test Suite for Oncology - Melanoma Rule.
"""

from app.enterprise.generated_rules.rule_oncology_melanoma import MelanomaClinicalRuleProcessor


def test_melanoma_rule_evaluation():
    processor = MelanomaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_melanoma": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_MELANOMA"

    res_pass = processor.evaluate({"has_melanoma": False})
    assert res_pass["passed"] is True
