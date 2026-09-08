"""
Test Suite for Hematology - AplasticAnemia Rule.
"""

from app.enterprise.generated_rules.rule_hematology_aplasticanemia import AplasticAnemiaClinicalRuleProcessor


def test_aplasticanemia_rule_evaluation():
    processor = AplasticAnemiaClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_aplasticanemia": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_HEMATOLOGY_APLASTICANEMIA"

    res_pass = processor.evaluate({"has_aplasticanemia": False})
    assert res_pass["passed"] is True
