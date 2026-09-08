"""
Test Suite for Endocrinology - Type2Diabetes Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_type2diabetes import Type2DiabetesClinicalRuleProcessor


def test_type2diabetes_rule_evaluation():
    processor = Type2DiabetesClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_type2diabetes": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_TYPE2DIABETES"

    res_pass = processor.evaluate({"has_type2diabetes": False})
    assert res_pass["passed"] is True
