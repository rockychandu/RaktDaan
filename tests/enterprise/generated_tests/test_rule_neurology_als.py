"""
Test Suite for Neurology - ALS Rule.
"""

from app.enterprise.generated_rules.rule_neurology_als import ALSClinicalRuleProcessor


def test_als_rule_evaluation():
    processor = ALSClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_als": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_ALS"

    res_pass = processor.evaluate({"has_als": False})
    assert res_pass["passed"] is True
