from typing import List
from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.oversight.convergence.models import ConvergenceAssessment, ConvergenceStatus, StabilityMetric

class ConvergenceEngine:
    """
    Determines whether the executive reasoning process has stabilized.
    """
    def evaluate_convergence(self, historical_decisions: List[ExecutiveDecision], current_decision: ExecutiveDecision) -> ConvergenceAssessment:
        if not historical_decisions:
            return ConvergenceAssessment(
                status=ConvergenceStatus.PROGRESSING,
                confidence=0.1,
                metrics=[StabilityMetric(metric_name="decision_delta", value=1.0)]
            )
            
        last_decision = historical_decisions[-1]
        
        if last_decision.selected_alternative_id == current_decision.selected_alternative_id:
            return ConvergenceAssessment(
                status=ConvergenceStatus.CONVERGED,
                confidence=0.9,
                metrics=[StabilityMetric(metric_name="decision_delta", value=0.0)]
            )
            
        # If decisions are alternating between two options, mark as oscillating
        if len(historical_decisions) >= 2:
            prev_prev_decision = historical_decisions[-2]
            if prev_prev_decision.selected_alternative_id == current_decision.selected_alternative_id:
                return ConvergenceAssessment(
                    status=ConvergenceStatus.OSCILLATING,
                    confidence=0.5,
                    metrics=[StabilityMetric(metric_name="decision_delta", value=1.0)]
                )
                
        return ConvergenceAssessment(
            status=ConvergenceStatus.PROGRESSING,
            confidence=0.5,
            metrics=[StabilityMetric(metric_name="decision_delta", value=0.5)]
        )
