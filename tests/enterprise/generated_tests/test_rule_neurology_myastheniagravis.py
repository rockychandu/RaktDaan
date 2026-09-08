"""
Test Suite for Neurology - MyastheniaGravis Rule.
"""

from app.enterprise.generated_rules.rule_neurology_myastheniagravis import MyastheniaGravisClinicalRuleProcessor


def test_myastheniagravis_rule_evaluation():
    processor = MyastheniaGravisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_myastheniagravis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_MYASTHENIAGRAVIS"

    res_pass = processor.evaluate({"has_myastheniagravis": False})
    assert res_pass["passed"] is True
