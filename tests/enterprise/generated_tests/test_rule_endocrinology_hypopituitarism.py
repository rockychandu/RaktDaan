"""
Test Suite for Endocrinology - Hypopituitarism Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_hypopituitarism import HypopituitarismClinicalRuleProcessor


def test_hypopituitarism_rule_evaluation():
    processor = HypopituitarismClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_hypopituitarism": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_HYPOPITUITARISM"

    res_pass = processor.evaluate({"has_hypopituitarism": False})
    assert res_pass["passed"] is True
