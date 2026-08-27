"""
Test Suite for Surgery - CornealTransplant Rule.
"""

from app.enterprise.generated_rules.rule_surgery_cornealtransplant import CornealTransplantClinicalRuleProcessor


def test_cornealtransplant_rule_evaluation():
    processor = CornealTransplantClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cornealtransplant": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_CORNEALTRANSPLANT"

    res_pass = processor.evaluate({"has_cornealtransplant": False})
    assert res_pass["passed"] is True
