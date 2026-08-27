"""
Test Suite for Toxicology - HeavyMetalToxicity Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_heavymetaltoxicity import HeavyMetalToxicityClinicalRuleProcessor


def test_heavymetaltoxicity_rule_evaluation():
    processor = HeavyMetalToxicityClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_heavymetaltoxicity": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_HEAVYMETALTOXICITY"

    res_pass = processor.evaluate({"has_heavymetaltoxicity": False})
    assert res_pass["passed"] is True
