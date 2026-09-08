"""
Test Suite for Immunology - Vasculitis Rule.
"""

from app.enterprise.generated_rules.rule_immunology_vasculitis import VasculitisClinicalRuleProcessor


def test_vasculitis_rule_evaluation():
    processor = VasculitisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_vasculitis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_VASCULITIS"

    res_pass = processor.evaluate({"has_vasculitis": False})
    assert res_pass["passed"] is True
