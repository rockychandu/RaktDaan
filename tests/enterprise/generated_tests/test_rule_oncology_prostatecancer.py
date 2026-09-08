"""
Test Suite for Oncology - ProstateCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_prostatecancer import ProstateCancerClinicalRuleProcessor


def test_prostatecancer_rule_evaluation():
    processor = ProstateCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_prostatecancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_PROSTATECANCER"

    res_pass = processor.evaluate({"has_prostatecancer": False})
    assert res_pass["passed"] is True
