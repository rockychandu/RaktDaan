"""
Test Suite for Gastroenterology - BarrettsEsophagus Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_barrettsesophagus import BarrettsEsophagusClinicalRuleProcessor


def test_barrettsesophagus_rule_evaluation():
    processor = BarrettsEsophagusClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_barrettsesophagus": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_BARRETTSESOPHAGUS"

    res_pass = processor.evaluate({"has_barrettsesophagus": False})
    assert res_pass["passed"] is True
