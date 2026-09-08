"""
Automated Unit Test Suite for Advanced Enterprise Clinical Rules & Toxicology.
"""

from app.enterprise.clinical_rules.dermatology_topical_rules import (
    PsoriasisEczemaLesionRule, SystemicEtretinateRule
)
from app.enterprise.clinical_rules.ophthalmology_surgery_rules import CornealGraftRule
from app.enterprise.clinical_rules.dentistry_extraction_rules import DentalExtractionScalingRule
from app.enterprise.clinical_rules.toxicology_substance_rules import (
    IntravenousSubstanceRule, AlcoholIntoxicationRule
)


def test_dermatology_rules():
    assert PsoriasisEczemaLesionRule().evaluate({"has_antecubital_skin_lesion": True})["passed"] is False
    assert SystemicEtretinateRule().evaluate({"ever_took_etretinate_tegison": True})["passed"] is False


def test_corneal_graft_rule():
    assert CornealGraftRule().evaluate({"has_corneal_transplant": True})["passed"] is False
    assert CornealGraftRule().evaluate({"has_corneal_transplant": False})["passed"] is True


def test_dentistry_rule():
    assert DentalExtractionScalingRule().evaluate({"had_tooth_extraction_past_7d": True})["passed"] is False
    assert DentalExtractionScalingRule().evaluate({"had_tooth_extraction_past_7d": False})["passed"] is True


def test_toxicology_rules():
    assert IntravenousSubstanceRule().evaluate({"has_iv_drug_use_history": True})["passed"] is False
    assert AlcoholIntoxicationRule().evaluate({"is_acutely_intoxicated": True})["passed"] is False
