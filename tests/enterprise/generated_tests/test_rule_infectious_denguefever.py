"""
Test Suite for Infectious - DengueFever Rule.
"""

from app.enterprise.generated_rules.rule_infectious_denguefever import DengueFeverClinicalRuleProcessor


def test_denguefever_rule_evaluation():
    processor = DengueFeverClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_denguefever": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_DENGUEFEVER"

    res_pass = processor.evaluate({"has_denguefever": False})
    assert res_pass["passed"] is True
