"""
Test Suite for Endocrinology - Type1Diabetes Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_type1diabetes import Type1DiabetesClinicalRuleProcessor


def test_type1diabetes_rule_evaluation():
    processor = Type1DiabetesClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_type1diabetes": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_TYPE1DIABETES"

    res_pass = processor.evaluate({"has_type1diabetes": False})
    assert res_pass["passed"] is True
