"""
Test Suite for Nephrology - CKDStage2 Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_ckdstage2 import CKDStage2ClinicalRuleProcessor


def test_ckdstage2_rule_evaluation():
    processor = CKDStage2ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ckdstage2": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_CKDSTAGE2"

    res_pass = processor.evaluate({"has_ckdstage2": False})
    assert res_pass["passed"] is True
