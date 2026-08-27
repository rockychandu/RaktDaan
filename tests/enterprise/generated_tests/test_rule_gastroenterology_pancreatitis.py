"""
Test Suite for Gastroenterology - Pancreatitis Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_pancreatitis import PancreatitisClinicalRuleProcessor


def test_pancreatitis_rule_evaluation():
    processor = PancreatitisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_pancreatitis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_PANCREATITIS"

    res_pass = processor.evaluate({"has_pancreatitis": False})
    assert res_pass["passed"] is True
