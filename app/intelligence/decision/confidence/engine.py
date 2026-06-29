from app.intelligence.decision.confidence.models import ConfidenceAssessment, ConfidenceScore, EvidenceWeight
from app.intelligence.decision.uncertainty.models import UncertaintyAssessment

class ConfidenceEngine:
    """
    Evaluates confidence scores for decisions.
    """
    def evaluate_confidence(self, uncertainty: UncertaintyAssessment) -> ConfidenceAssessment:
        # Confidence is inversely related to uncertainty
        overall = 1.0 - uncertainty.overall_uncertainty_score
        
        return ConfidenceAssessment(
            overall_score=overall,
            scores=[ConfidenceScore(category="SimulationQuality", score=0.8)],
            evidence_weights=[EvidenceWeight(evidence_id="e1", weight=0.5)],
            is_actionable=(overall >= 0.5)
        )
