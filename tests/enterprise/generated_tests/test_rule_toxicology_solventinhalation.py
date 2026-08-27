"""
Test Suite for Toxicology - SolventInhalation Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_solventinhalation import SolventInhalationClinicalRuleProcessor


def test_solventinhalation_rule_evaluation():
    processor = SolventInhalationClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_solventinhalation": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_SOLVENTINHALATION"

    res_pass = processor.evaluate({"has_solventinhalation": False})
    assert res_pass["passed"] is True
