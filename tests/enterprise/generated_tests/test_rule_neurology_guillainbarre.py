"""
Test Suite for Neurology - GuillainBarre Rule.
"""

from app.enterprise.generated_rules.rule_neurology_guillainbarre import GuillainBarreClinicalRuleProcessor


def test_guillainbarre_rule_evaluation():
    processor = GuillainBarreClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_guillainbarre": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_GUILLAINBARRE"

    res_pass = processor.evaluate({"has_guillainbarre": False})
    assert res_pass["passed"] is True
