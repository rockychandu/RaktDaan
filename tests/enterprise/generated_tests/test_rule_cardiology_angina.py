"""
Test Suite for Cardiology - Angina Rule.
"""

from app.enterprise.generated_rules.rule_cardiology_angina import AnginaClinicalRuleProcessor


def test_angina_rule_evaluation():
    processor = AnginaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_angina": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_CARDIOLOGY_ANGINA"

    res_pass = processor.evaluate({"has_angina": False})
    assert res_pass["passed"] is True
