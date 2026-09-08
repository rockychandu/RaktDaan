"""
Test Suite for Nephrology - CKDStage4 Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_ckdstage4 import CKDStage4ClinicalRuleProcessor


def test_ckdstage4_rule_evaluation():
    processor = CKDStage4ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ckdstage4": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_CKDSTAGE4"

    res_pass = processor.evaluate({"has_ckdstage4": False})
    assert res_pass["passed"] is True
