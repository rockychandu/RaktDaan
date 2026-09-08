"""
Test Suite for Nephrology - CKDStage3 Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_ckdstage3 import CKDStage3ClinicalRuleProcessor


def test_ckdstage3_rule_evaluation():
    processor = CKDStage3ClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ckdstage3": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_CKDSTAGE3"

    res_pass = processor.evaluate({"has_ckdstage3": False})
    assert res_pass["passed"] is True
