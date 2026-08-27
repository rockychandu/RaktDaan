"""
Test Suite for Endocrinology - Hashimotos Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_hashimotos import HashimotosClinicalRuleProcessor


def test_hashimotos_rule_evaluation():
    processor = HashimotosClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hashimotos": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_HASHIMOTOS"

    res_pass = processor.evaluate({"has_hashimotos": False})
    assert res_pass["passed"] is True
