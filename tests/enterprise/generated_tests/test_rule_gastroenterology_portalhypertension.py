"""
Test Suite for Gastroenterology - PortalHypertension Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_portalhypertension import PortalHypertensionClinicalRuleProcessor


def test_portalhypertension_rule_evaluation():
    processor = PortalHypertensionClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_portalhypertension": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_PORTALHYPERTENSION"

    res_pass = processor.evaluate({"has_portalhypertension": False})
    assert res_pass["passed"] is True
