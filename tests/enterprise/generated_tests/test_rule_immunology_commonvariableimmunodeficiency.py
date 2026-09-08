"""
Test Suite for Immunology - CommonVariableImmunodeficiency Rule.
"""

from app.enterprise.generated_rules.rule_immunology_commonvariableimmunodeficiency import CommonVariableImmunodeficiencyClinicalRuleProcessor


def test_commonvariableimmunodeficiency_rule_evaluation():
    processor = CommonVariableImmunodeficiencyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_commonvariableimmunodeficiency": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_COMMONVARIABLEIMMUNODEFICIENCY"

    res_pass = processor.evaluate({"has_commonvariableimmunodeficiency": False})
    assert res_pass["passed"] is True
