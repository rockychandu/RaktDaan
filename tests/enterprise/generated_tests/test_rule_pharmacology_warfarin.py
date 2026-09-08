"""
Test Suite for Pharmacology - Warfarin Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_warfarin import WarfarinClinicalRuleProcessor


def test_warfarin_rule_evaluation():
    processor = WarfarinClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_warfarin": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_WARFARIN"

    res_pass = processor.evaluate({"has_warfarin": False})
    assert res_pass["passed"] is True
