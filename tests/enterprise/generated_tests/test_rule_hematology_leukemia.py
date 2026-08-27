"""
Test Suite for Hematology - Leukemia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_leukemia import LeukemiaClinicalRuleProcessor


def test_leukemia_rule_evaluation():
    processor = LeukemiaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_leukemia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_LEUKEMIA"

    res_pass = processor.evaluate({"has_leukemia": False})
    assert res_pass["passed"] is True
