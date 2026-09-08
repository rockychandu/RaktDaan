"""
Test Suite for Toxicology - CocaineExposure Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_cocaineexposure import CocaineExposureClinicalRuleProcessor


def test_cocaineexposure_rule_evaluation():
    processor = CocaineExposureClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cocaineexposure": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_COCAINEEXPOSURE"

    res_pass = processor.evaluate({"has_cocaineexposure": False})
    assert res_pass["passed"] is True
