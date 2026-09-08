"""
Test Suite for Nephrology - RenalTransplant Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_renaltransplant import RenalTransplantClinicalRuleProcessor


def test_renaltransplant_rule_evaluation():
    processor = RenalTransplantClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_renaltransplant": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_RENALTRANSPLANT"

    res_pass = processor.evaluate({"has_renaltransplant": False})
    assert res_pass["passed"] is True
