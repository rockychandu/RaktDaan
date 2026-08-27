"""
Test Suite for Infectious - Malaria Rule.
"""

from app.enterprise.generated_rules.rule_infectious_malaria import MalariaClinicalRuleProcessor


def test_malaria_rule_evaluation():
    processor = MalariaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_malaria": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_MALARIA"

    res_pass = processor.evaluate({"has_malaria": False})
    assert res_pass["passed"] is True
