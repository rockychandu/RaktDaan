"""
Test Suite for Oncology - Glioblastoma Rule.
"""

from app.enterprise.generated_rules.rule_oncology_glioblastoma import GlioblastomaClinicalRuleProcessor


def test_glioblastoma_rule_evaluation():
    processor = GlioblastomaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_glioblastoma": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_GLIOBLASTOMA"

    res_pass = processor.evaluate({"has_glioblastoma": False})
    assert res_pass["passed"] is True
