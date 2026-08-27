"""
Test Suite for Infectious - Tuberculosis Rule.
"""

from app.enterprise.generated_rules.rule_infectious_tuberculosis import TuberculosisClinicalRuleProcessor


def test_tuberculosis_rule_evaluation():
    processor = TuberculosisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_tuberculosis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_TUBERCULOSIS"

    res_pass = processor.evaluate({"has_tuberculosis": False})
    assert res_pass["passed"] is True
