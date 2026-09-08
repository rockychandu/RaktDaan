"""
Test Suite for Neurology - Epilepsy Rule.
"""

from app.enterprise.generated_rules.rule_neurology_epilepsy import EpilepsyClinicalRuleProcessor


def test_epilepsy_rule_evaluation():
    processor = EpilepsyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_epilepsy": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEUROLOGY_EPILEPSY"

    res_pass = processor.evaluate({"has_epilepsy": False})
    assert res_pass["passed"] is True
