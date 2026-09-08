"""
Test Suite for Gastroenterology - Cirrhosis Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_cirrhosis import CirrhosisClinicalRuleProcessor


def test_cirrhosis_rule_evaluation():
    processor = CirrhosisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cirrhosis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_CIRRHOSIS"

    res_pass = processor.evaluate({"has_cirrhosis": False})
    assert res_pass["passed"] is True
