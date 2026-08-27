"""
Test Suite for Surgery - DuraMaterGraft Rule.
"""

from app.enterprise.generated_rules.rule_surgery_duramatergraft import DuraMaterGraftClinicalRuleProcessor


def test_duramatergraft_rule_evaluation():
    processor = DuraMaterGraftClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_duramatergraft": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_SURGERY_DURAMATERGRAFT"

    res_pass = processor.evaluate({"has_duramatergraft": False})
    assert res_pass["passed"] is True
