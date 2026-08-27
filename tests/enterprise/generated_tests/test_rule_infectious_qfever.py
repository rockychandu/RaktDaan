"""
Test Suite for Infectious - QFever Rule.
"""

from app.enterprise.generated_rules.rule_infectious_qfever import QFeverClinicalRuleProcessor


def test_qfever_rule_evaluation():
    processor = QFeverClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_qfever": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_INFECTIOUS_QFEVER"

    res_pass = processor.evaluate({"has_qfever": False})
    assert res_pass["passed"] is True
