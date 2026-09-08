"""
Test Suite for Hematology - SickleCell Rule.
"""

from app.enterprise.generated_rules.rule_hematology_sicklecell import SickleCellClinicalRuleProcessor


def test_sicklecell_rule_evaluation():
    processor = SickleCellClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_sicklecell": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_SICKLECELL"

    res_pass = processor.evaluate({"has_sicklecell": False})
    assert res_pass["passed"] is True
