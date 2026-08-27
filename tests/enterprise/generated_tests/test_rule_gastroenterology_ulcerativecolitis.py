"""
Test Suite for Gastroenterology - UlcerativeColitis Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_ulcerativecolitis import UlcerativeColitisClinicalRuleProcessor


def test_ulcerativecolitis_rule_evaluation():
    processor = UlcerativeColitisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ulcerativecolitis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_ULCERATIVECOLITIS"

    res_pass = processor.evaluate({"has_ulcerativecolitis": False})
    assert res_pass["passed"] is True
