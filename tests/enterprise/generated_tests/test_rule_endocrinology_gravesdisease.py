"""
Test Suite for Endocrinology - GravesDisease Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_gravesdisease import GravesDiseaseClinicalRuleProcessor


def test_gravesdisease_rule_evaluation():
    processor = GravesDiseaseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_gravesdisease": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_GRAVESDISEASE"

    res_pass = processor.evaluate({"has_gravesdisease": False})
    assert res_pass["passed"] is True
