"""
Test Suite for Oncology - BladderCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_bladdercancer import BladderCancerClinicalRuleProcessor


def test_bladdercancer_rule_evaluation():
    processor = BladderCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_bladdercancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_BLADDERCANCER"

    res_pass = processor.evaluate({"has_bladdercancer": False})
    assert res_pass["passed"] is True
