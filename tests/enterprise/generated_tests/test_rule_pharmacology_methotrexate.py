"""
Test Suite for Pharmacology - Methotrexate Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_methotrexate import MethotrexateClinicalRuleProcessor


def test_methotrexate_rule_evaluation():
    processor = MethotrexateClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_methotrexate": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_METHOTREXATE"

    res_pass = processor.evaluate({"has_methotrexate": False})
    assert res_pass["passed"] is True
