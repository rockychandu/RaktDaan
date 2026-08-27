"""
Test Suite for Pharmacology - Etretinate Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_etretinate import EtretinateClinicalRuleProcessor


def test_etretinate_rule_evaluation():
    processor = EtretinateClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_etretinate": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_ETRETINATE"

    res_pass = processor.evaluate({"has_etretinate": False})
    assert res_pass["passed"] is True
