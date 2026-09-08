"""
Test Suite for Cardiology - CoronaryStent Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_coronarystent import CoronaryStentClinicalRuleProcessor


def test_coronarystent_rule_evaluation():
    processor = CoronaryStentClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_coronarystent": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_CORONARYSTENT"

    res_pass = processor.evaluate({"has_coronarystent": False})
    assert res_pass["passed"] is True
