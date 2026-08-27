"""
Test Suite for Hematology - Hemochromatosis Rule.
"""

from app.enterprise.generated_rules.rule_hematology_hemochromatosis import HemochromatosisClinicalRuleProcessor


def test_hemochromatosis_rule_evaluation():
    processor = HemochromatosisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hemochromatosis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_HEMOCHROMATOSIS"

    res_pass = processor.evaluate({"has_hemochromatosis": False})
    assert res_pass["passed"] is True
