from app.intelligence.decision.uncertainty.engine import UncertaintyEngine
from app.intelligence.decision.uncertainty.models import UncertaintySource

def test_estimate_uncertainty():
    engine = UncertaintyEngine()
    
    assessment = engine.estimate_uncertainty()
    
    assert assessment.overall_uncertainty_score == 0.4
    assert len(assessment.sources) == 1
    assert assessment.sources[0] == UncertaintySource.UNPROVEN_ASSUMPTION
    assert len(assessment.assumptions) == 1
    assert assessment.assumptions[0].assumption_id == "a1"
    assert assessment.missing_evidence_ids == ["e1_missing"]
