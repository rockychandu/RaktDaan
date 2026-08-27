"""
Test Suite for Endocrinology - Hyperparathyroidism Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_hyperparathyroidism import HyperparathyroidismClinicalRuleProcessor


def test_hyperparathyroidism_rule_evaluation():
    processor = HyperparathyroidismClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hyperparathyroidism": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_HYPERPARATHYROIDISM"

    res_pass = processor.evaluate({"has_hyperparathyroidism": False})
    assert res_pass["passed"] is True
