"""
Test Suite for Pharmacology - Dutasteride Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_dutasteride import DutasterideClinicalRuleProcessor


def test_dutasteride_rule_evaluation():
    processor = DutasterideClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_dutasteride": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_DUTASTERIDE"

    res_pass = processor.evaluate({"has_dutasteride": False})
    assert res_pass["passed"] is True
