"""
Test Suite for Surgery - OrganTransplant Rule.
"""

from app.enterprise.generated_rules.rule_surgery_organtransplant import OrganTransplantClinicalRuleProcessor


def test_organtransplant_rule_evaluation():
    processor = OrganTransplantClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_organtransplant": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_ORGANTRANSPLANT"

    res_pass = processor.evaluate({"has_organtransplant": False})
    assert res_pass["passed"] is True
