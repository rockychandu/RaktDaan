"""
Test Suite for Toxicology - AlcoholIntoxication Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_alcoholintoxication import AlcoholIntoxicationClinicalRuleProcessor


def test_alcoholintoxication_rule_evaluation():
    processor = AlcoholIntoxicationClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_alcoholintoxication": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_ALCOHOLINTOXICATION"

    res_pass = processor.evaluate({"has_alcoholintoxication": False})
    assert res_pass["passed"] is True
