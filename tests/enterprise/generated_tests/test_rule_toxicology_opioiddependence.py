"""
Test Suite for Toxicology - OpioidDependence Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_opioiddependence import OpioidDependenceClinicalRuleProcessor


def test_opioiddependence_rule_evaluation():
    processor = OpioidDependenceClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_opioiddependence": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_OPIOIDDEPENDENCE"

    res_pass = processor.evaluate({"has_opioiddependence": False})
    assert res_pass["passed"] is True
