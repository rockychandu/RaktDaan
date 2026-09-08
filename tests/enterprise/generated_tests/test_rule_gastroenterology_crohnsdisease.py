"""
Test Suite for Gastroenterology - CrohnsDisease Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_crohnsdisease import CrohnsDiseaseClinicalRuleProcessor


def test_crohnsdisease_rule_evaluation():
    processor = CrohnsDiseaseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_crohnsdisease": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_CROHNSDISEASE"

    res_pass = processor.evaluate({"has_crohnsdisease": False})
    assert res_pass["passed"] is True
