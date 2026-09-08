"""
Test Suite for Endocrinology - Pheochromocytoma Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_pheochromocytoma import PheochromocytomaClinicalRuleProcessor


def test_pheochromocytoma_rule_evaluation():
    processor = PheochromocytomaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_pheochromocytoma": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_PHEOCHROMOCYTOMA"

    res_pass = processor.evaluate({"has_pheochromocytoma": False})
    assert res_pass["passed"] is True
