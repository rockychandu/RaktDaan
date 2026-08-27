"""
Test Suite for Oncology - RenalCellCarcinoma Rule.
"""

from app.enterprise.generated_rules.rule_oncology_renalcellcarcinoma import RenalCellCarcinomaClinicalRuleProcessor


def test_renalcellcarcinoma_rule_evaluation():
    processor = RenalCellCarcinomaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_renalcellcarcinoma": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_RENALCELLCARCINOMA"

    res_pass = processor.evaluate({"has_renalcellcarcinoma": False})
    assert res_pass["passed"] is True
