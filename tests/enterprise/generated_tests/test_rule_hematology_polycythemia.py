"""
Test Suite for Hematology - Polycythemia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_polycythemia import PolycythemiaClinicalRuleProcessor


def test_polycythemia_rule_evaluation():
    processor = PolycythemiaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_polycythemia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_POLYCYTHEMIA"

    res_pass = processor.evaluate({"has_polycythemia": False})
    assert res_pass["passed"] is True
