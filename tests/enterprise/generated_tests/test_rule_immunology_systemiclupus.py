"""
Test Suite for Immunology - SystemicLupus Rule.
"""

from app.enterprise.generated_rules.rule_immunology_systemiclupus import SystemicLupusClinicalRuleProcessor


def test_systemiclupus_rule_evaluation():
    processor = SystemicLupusClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_systemiclupus": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_SYSTEMICLUPUS"

    res_pass = processor.evaluate({"has_systemiclupus": False})
    assert res_pass["passed"] is True
