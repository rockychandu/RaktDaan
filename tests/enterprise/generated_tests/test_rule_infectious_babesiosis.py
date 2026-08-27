"""
Test Suite for Infectious - Babesiosis Rule.
"""

from app.enterprise.generated_rules.rule_infectious_babesiosis import BabesiosisClinicalRuleProcessor


def test_babesiosis_rule_evaluation():
    processor = BabesiosisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_babesiosis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_BABESIOSIS"

    res_pass = processor.evaluate({"has_babesiosis": False})
    assert res_pass["passed"] is True
