"""
Test Suite for Gastroenterology - HepaticEncephalopathy Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_hepaticencephalopathy import HepaticEncephalopathyClinicalRuleProcessor


def test_hepaticencephalopathy_rule_evaluation():
    processor = HepaticEncephalopathyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hepaticencephalopathy": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_HEPATICENCEPHALOPATHY"

    res_pass = processor.evaluate({"has_hepaticencephalopathy": False})
    assert res_pass["passed"] is True
