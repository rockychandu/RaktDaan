"""
Test Suite for Gastroenterology - CeliacDisease Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_celiacdisease import CeliacDiseaseClinicalRuleProcessor


def test_celiacdisease_rule_evaluation():
    processor = CeliacDiseaseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_celiacdisease": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_CELIACDISEASE"

    res_pass = processor.evaluate({"has_celiacdisease": False})
    assert res_pass["passed"] is True
