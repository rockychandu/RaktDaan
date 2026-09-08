"""
Test Suite for Infectious - LymeDisease Rule.
"""

from app.enterprise.generated_rules.rule_infectious_lymedisease import LymeDiseaseClinicalRuleProcessor


def test_lymedisease_rule_evaluation():
    processor = LymeDiseaseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_lymedisease": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_LYMEDISEASE"

    res_pass = processor.evaluate({"has_lymedisease": False})
    assert res_pass["passed"] is True
