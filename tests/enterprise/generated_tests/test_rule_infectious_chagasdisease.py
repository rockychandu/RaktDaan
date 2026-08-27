"""
Test Suite for Infectious - ChagasDisease Rule.
"""

from app.enterprise.generated_rules.rule_infectious_chagasdisease import ChagasDiseaseClinicalRuleProcessor


def test_chagasdisease_rule_evaluation():
    processor = ChagasDiseaseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_chagasdisease": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_CHAGASDISEASE"

    res_pass = processor.evaluate({"has_chagasdisease": False})
    assert res_pass["passed"] is True
