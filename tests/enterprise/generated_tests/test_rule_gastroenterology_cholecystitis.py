"""
Test Suite for Gastroenterology - Cholecystitis Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_cholecystitis import CholecystitisClinicalRuleProcessor


def test_cholecystitis_rule_evaluation():
    processor = CholecystitisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cholecystitis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_CHOLECYSTITIS"

    res_pass = processor.evaluate({"has_cholecystitis": False})
    assert res_pass["passed"] is True
