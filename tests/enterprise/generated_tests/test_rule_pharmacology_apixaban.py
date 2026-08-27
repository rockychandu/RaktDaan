"""
Test Suite for Pharmacology - Apixaban Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_apixaban import ApixabanClinicalRuleProcessor


def test_apixaban_rule_evaluation():
    processor = ApixabanClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_apixaban": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_APIXABAN"

    res_pass = processor.evaluate({"has_apixaban": False})
    assert res_pass["passed"] is True
