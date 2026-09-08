"""
Test Suite for Nephrology - CKDStage5 Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_ckdstage5 import CKDStage5ClinicalRuleProcessor


def test_ckdstage5_rule_evaluation():
    processor = CKDStage5ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ckdstage5": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_CKDSTAGE5"

    res_pass = processor.evaluate({"has_ckdstage5": False})
    assert res_pass["passed"] is True
