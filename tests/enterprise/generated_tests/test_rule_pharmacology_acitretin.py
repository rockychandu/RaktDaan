"""
Test Suite for Pharmacology - Acitretin Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_acitretin import AcitretinClinicalRuleProcessor


def test_acitretin_rule_evaluation():
    processor = AcitretinClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_acitretin": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_ACITRETIN"

    res_pass = processor.evaluate({"has_acitretin": False})
    assert res_pass["passed"] is True
