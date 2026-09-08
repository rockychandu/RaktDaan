"""
Test Suite for Toxicology - BarbiturateUse Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_barbiturateuse import BarbiturateUseClinicalRuleProcessor


def test_barbiturateuse_rule_evaluation():
    processor = BarbiturateUseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_barbiturateuse": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_BARBITURATEUSE"

    res_pass = processor.evaluate({"has_barbiturateuse": False})
    assert res_pass["passed"] is True
