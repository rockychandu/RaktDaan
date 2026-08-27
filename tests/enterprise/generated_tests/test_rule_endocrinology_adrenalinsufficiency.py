"""
Test Suite for Endocrinology - AdrenalInsufficiency Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_adrenalinsufficiency import AdrenalInsufficiencyClinicalRuleProcessor


def test_adrenalinsufficiency_rule_evaluation():
    processor = AdrenalInsufficiencyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_adrenalinsufficiency": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_ADRENALINSUFFICIENCY"

    res_pass = processor.evaluate({"has_adrenalinsufficiency": False})
    assert res_pass["passed"] is True
