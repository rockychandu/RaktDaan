"""
Test Suite for Hematology - Anemia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_anemia import AnemiaClinicalRuleProcessor


def test_anemia_rule_evaluation():
    processor = AnemiaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_anemia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_ANEMIA"

    res_pass = processor.evaluate({"has_anemia": False})
    assert res_pass["passed"] is True
