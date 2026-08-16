from app.intelligence.decision.confidence.engine import ConfidenceEngine
from app.intelligence.decision.uncertainty.models import UncertaintyAssessment


def test_evaluate_confidence():
    engine = ConfidenceEngine()

    uncertainty = UncertaintyAssessment(
        overall_uncertainty_score=0.3, sources=[], assumptions=[], missing_evidence_ids=[]
    )

    assessment = engine.evaluate_confidence(uncertainty)

    assert assessment.overall_score == 0.7  # 1.0 - 0.3
    assert assessment.is_actionable is True
    assert len(assessment.scores) == 1
    assert assessment.scores[0].category == "SimulationQuality"
    assert len(assessment.evidence_weights) == 1
    assert assessment.evidence_weights[0].evidence_id == "e1"


def test_evaluate_low_confidence():
    engine = ConfidenceEngine()

    uncertainty = UncertaintyAssessment(
        overall_uncertainty_score=0.8, sources=[], assumptions=[], missing_evidence_ids=[]
    )

    assessment = engine.evaluate_confidence(uncertainty)

    import pytest

    assert assessment.overall_score == pytest.approx(0.2)  # 1.0 - 0.8
    assert assessment.is_actionable is False
