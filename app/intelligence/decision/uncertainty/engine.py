from app.intelligence.decision.uncertainty.models import UncertaintyAssessment, UncertaintySource, Assumption

class UncertaintyEngine:
    """
    Estimates missing information and detects assumptions.
    """
    def estimate_uncertainty(self) -> UncertaintyAssessment:
        # Mock logic
        return UncertaintyAssessment(
            overall_uncertainty_score=0.4,
            sources=[UncertaintySource.UNPROVEN_ASSUMPTION],
            assumptions=[Assumption(assumption_id="a1", description="Market conditions will remain stable", confidence_level=0.6)],
            missing_evidence_ids=["e1_missing"]
        )
