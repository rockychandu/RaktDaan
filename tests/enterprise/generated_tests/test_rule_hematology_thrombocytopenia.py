"""
Test Suite for Hematology - Thrombocytopenia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_thrombocytopenia import ThrombocytopeniaClinicalRuleProcessor


def test_thrombocytopenia_rule_evaluation():
    processor = ThrombocytopeniaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_thrombocytopenia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_THROMBOCYTOPENIA"

    res_pass = processor.evaluate({"has_thrombocytopenia": False})
    assert res_pass["passed"] is True
