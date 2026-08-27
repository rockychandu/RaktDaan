"""
Test Suite for Infectious - HTLV Rule.
"""

from app.enterprise.generated_rules.rule_infectious_htlv import HTLVClinicalRuleProcessor


def test_htlv_rule_evaluation():
    processor = HTLVClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_htlv": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_HTLV"

    res_pass = processor.evaluate({"has_htlv": False})
    assert res_pass["passed"] is True
