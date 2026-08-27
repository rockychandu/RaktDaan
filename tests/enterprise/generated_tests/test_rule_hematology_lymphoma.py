"""
Test Suite for Hematology - Lymphoma Rule.
"""

from app.enterprise.generated_rules.rule_hematology_lymphoma import LymphomaClinicalRuleProcessor


def test_lymphoma_rule_evaluation():
    processor = LymphomaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_lymphoma": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_LYMPHOMA"

    res_pass = processor.evaluate({"has_lymphoma": False})
    assert res_pass["passed"] is True
