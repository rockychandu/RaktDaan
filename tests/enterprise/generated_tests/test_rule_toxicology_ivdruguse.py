"""
Test Suite for Toxicology - IVDrugUse Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_ivdruguse import IVDrugUseClinicalRuleProcessor


def test_ivdruguse_rule_evaluation():
    processor = IVDrugUseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ivdruguse": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_IVDRUGUSE"

    res_pass = processor.evaluate({"has_ivdruguse": False})
    assert res_pass["passed"] is True
