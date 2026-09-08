"""
Test Suite for Surgery - OrthopedicJointReplacement Rule.
"""

from app.enterprise.generated_rules.rule_surgery_orthopedicjointreplacement import OrthopedicJointReplacementClinicalRuleProcessor


def test_orthopedicjointreplacement_rule_evaluation():
    processor = OrthopedicJointReplacementClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_orthopedicjointreplacement": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_ORTHOPEDICJOINTREPLACEMENT"

    res_pass = processor.evaluate({"has_orthopedicjointreplacement": False})
    assert res_pass["passed"] is True
