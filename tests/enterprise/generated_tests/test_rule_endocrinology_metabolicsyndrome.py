"""
Test Suite for Endocrinology - MetabolicSyndrome Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_metabolicsyndrome import MetabolicSyndromeClinicalRuleProcessor


def test_metabolicsyndrome_rule_evaluation():
    processor = MetabolicSyndromeClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_metabolicsyndrome": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_METABOLICSYNDROME"

    res_pass = processor.evaluate({"has_metabolicsyndrome": False})
    assert res_pass["passed"] is True
