"""
Test Suite for Nephrology - PolycysticKidney Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_polycystickidney import PolycysticKidneyClinicalRuleProcessor


def test_polycystickidney_rule_evaluation():
    processor = PolycysticKidneyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_polycystickidney": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_POLYCYSTICKIDNEY"

    res_pass = processor.evaluate({"has_polycystickidney": False})
    assert res_pass["passed"] is True
