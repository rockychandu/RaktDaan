"""
Test Suite for Hematology - Hemophilia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_hemophilia import HemophiliaClinicalRuleProcessor


def test_hemophilia_rule_evaluation():
    processor = HemophiliaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hemophilia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_HEMOPHILIA"

    res_pass = processor.evaluate({"has_hemophilia": False})
    assert res_pass["passed"] is True
