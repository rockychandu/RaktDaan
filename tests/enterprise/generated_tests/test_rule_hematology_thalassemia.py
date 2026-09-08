"""
Test Suite for Hematology - Thalassemia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_thalassemia import ThalassemiaClinicalRuleProcessor


def test_thalassemia_rule_evaluation():
    processor = ThalassemiaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_thalassemia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_THALASSEMIA"

    res_pass = processor.evaluate({"has_thalassemia": False})
    assert res_pass["passed"] is True
