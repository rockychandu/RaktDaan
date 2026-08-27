"""
Test Suite for Surgery - TissueGraft Rule.
"""

from app.enterprise.generated_rules.rule_surgery_tissuegraft import TissueGraftClinicalRuleProcessor


def test_tissuegraft_rule_evaluation():
    processor = TissueGraftClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_tissuegraft": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_TISSUEGRAFT"

    res_pass = processor.evaluate({"has_tissuegraft": False})
    assert res_pass["passed"] is True
