"""
Test Suite for Nephrology - CKDStage1 Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_ckdstage1 import CKDStage1ClinicalRuleProcessor


def test_ckdstage1_rule_evaluation():
    processor = CKDStage1ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ckdstage1": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_CKDSTAGE1"

    res_pass = processor.evaluate({"has_ckdstage1": False})
    assert res_pass["passed"] is True
