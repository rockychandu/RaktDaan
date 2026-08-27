"""
Test Suite for Oncology - ColonCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_coloncancer import ColonCancerClinicalRuleProcessor


def test_coloncancer_rule_evaluation():
    processor = ColonCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_coloncancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_COLONCANCER"

    res_pass = processor.evaluate({"has_coloncancer": False})
    assert res_pass["passed"] is True
