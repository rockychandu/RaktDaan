"""
Test Suite for Gastroenterology - PepticUlcer Rule.
"""

from app.enterprise.generated_rules.rule_gastroenterology_pepticulcer import PepticUlcerClinicalRuleProcessor


def test_pepticulcer_rule_evaluation():
    processor = PepticUlcerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_pepticulcer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_GASTROENTEROLOGY_PEPTICULCER"

    res_pass = processor.evaluate({"has_pepticulcer": False})
    assert res_pass["passed"] is True
