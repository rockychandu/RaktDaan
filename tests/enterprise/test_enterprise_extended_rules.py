"""
Automated Unit Tests for Enterprise Extended Clinical Rules.
"""

from app.enterprise.clinical_rules.cardiology_extended_rules import (
    CardiomyopathyRule, CongestiveHeartFailureRule, MyocarditisPericarditisRule
)
from app.enterprise.clinical_rules.gastrointestinal_hepatic_rules import (
    InflammatoryBowelDiseaseRule, HepaticCirrhosisRule, GastrointestinalBleedingRule
)
from app.enterprise.clinical_rules.nephrology_dialysis_rules import (
    ChronicKidneyDiseaseRule, DialysisTherapyRule
)
from app.enterprise.clinical_rules.neurology_epilepsy_rules import (
    EpilepsySeizureRule, StrokeCerebrovascularRule
)


def test_cardiomyopathy_rule():
    rule = CardiomyopathyRule()
    assert rule.evaluate({"has_cardiomyopathy_diagnosis": True})["passed"] is False
    assert rule.evaluate({"has_cardiomyopathy_diagnosis": False})["passed"] is True


def test_ibd_rule():
    rule = InflammatoryBowelDiseaseRule()
    assert rule.evaluate({"has_crohns_disease": True})["passed"] is False
    assert rule.evaluate({"has_crohns_disease": False})["passed"] is True


def test_ckd_rule():
    rule = ChronicKidneyDiseaseRule()
    assert rule.evaluate({"has_chronic_kidney_disease": True})["passed"] is False
    assert rule.evaluate({"has_chronic_kidney_disease": False})["passed"] is True


def test_epilepsy_rule():
    rule = EpilepsySeizureRule()
    assert rule.evaluate({"has_epilepsy_diagnosis": True, "years_seizure_free_without_meds": 1.0})["passed"] is False
    assert rule.evaluate({"has_epilepsy_diagnosis": True, "years_seizure_free_without_meds": 4.0})["passed"] is True
