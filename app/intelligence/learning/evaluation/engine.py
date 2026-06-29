import uuid
from typing import Dict
from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.learning.evaluation.models import OutcomeEvaluation, OutcomeMetric, SuccessScore

class OutcomeEvaluationEngine:
    """
    Evaluates completed plans against their intended outcomes.
    """
    def evaluate_plan(self, plan: ExecutivePlan, actual_results: Dict[str, float]) -> OutcomeEvaluation:
        # Mock evaluation logic
        metrics = []
        score = SuccessScore.FAILED
        
        target = 100.0
        actual = actual_results.get("impact", 0.0)
        
        metrics.append(OutcomeMetric(metric_name="impact", target_value=target, actual_value=actual))
        
        if actual >= target:
            score = SuccessScore.ACHIEVED
        elif actual > 0:
            score = SuccessScore.PARTIAL
            
        return OutcomeEvaluation(
            evaluation_id=str(uuid.uuid4()),
            plan_id=plan.plan_id,
            overall_score=score,
            metrics=metrics
        )
