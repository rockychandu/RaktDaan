"""
Test Suite for Pharmacology - Isotretinoin Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_isotretinoin import IsotretinoinClinicalRuleProcessor


def test_isotretinoin_rule_evaluation():
    processor = IsotretinoinClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_isotretinoin": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_ISOTRETINOIN"

    res_pass = processor.evaluate({"has_isotretinoin": False})
    assert res_pass["passed"] is True
