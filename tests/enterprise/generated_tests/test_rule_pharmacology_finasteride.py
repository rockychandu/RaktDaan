"""
Test Suite for Pharmacology - Finasteride Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_finasteride import FinasterideClinicalRuleProcessor


def test_finasteride_rule_evaluation():
    processor = FinasterideClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_finasteride": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_FINASTERIDE"

    res_pass = processor.evaluate({"has_finasteride": False})
    assert res_pass["passed"] is True
