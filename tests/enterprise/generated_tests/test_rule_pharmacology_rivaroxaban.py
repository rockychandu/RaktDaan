"""
Test Suite for Pharmacology - Rivaroxaban Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_rivaroxaban import RivaroxabanClinicalRuleProcessor


def test_rivaroxaban_rule_evaluation():
    processor = RivaroxabanClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_rivaroxaban": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_RIVAROXABAN"

    res_pass = processor.evaluate({"has_rivaroxaban": False})
    assert res_pass["passed"] is True
