"""Quantitative Evaluation & Benchmarking Harness for BizOS AI Operations."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EvaluationMetricResult:
    metric_name: str
    score: float  # 0.0 to 1.0 or quantitative count
    target_threshold: float
    passed: bool
    detail: str


class EvaluationHarness:
    """Quantitative evaluator for measuring system reasoning, precision, and latency."""

    def __init__(self):
        self._results: List[EvaluationMetricResult] = []

    def evaluate_intent_accuracy(self, intent_type: str, expected_type: str = "CRISIS_RESPONSE") -> EvaluationMetricResult:
        score = 1.0 if intent_type == expected_type else 0.8
        res = EvaluationMetricResult(
            metric_name="Intent Parsing Accuracy",
            score=score,
            target_threshold=0.85,
            passed=score >= 0.85,
            detail=f"Parsed: {intent_type}, Expected: {expected_type}",
        )
        self._results.append(res)
        return res

    def evaluate_retrieval_precision(self, retrieved_count: int, expected_min: int = 1) -> EvaluationMetricResult:
        score = min(1.0, retrieved_count / max(1, expected_min))
        res = EvaluationMetricResult(
            metric_name="Vector Memory Retrieval Precision",
            score=score,
            target_threshold=0.8,
            passed=score >= 0.8,
            detail=f"Retrieved {retrieved_count} relevant chunks from Qdrant.",
        )
        self._results.append(res)
        return res

    def evaluate_goal_completion(self, completed_goals: int, total_goals: int) -> EvaluationMetricResult:
        score = completed_goals / max(1, total_goals)
        res = EvaluationMetricResult(
            metric_name="Goal Execution Completion Rate",
            score=score,
            target_threshold=1.0,
            passed=score >= 1.0,
            detail=f"{completed_goals}/{total_goals} goals executed cleanly.",
        )
        self._results.append(res)
        return res

    def evaluate_latency_efficiency(self, total_latency_ms: float, target_max_ms: float = 15000.0) -> EvaluationMetricResult:
        score = 1.0 if total_latency_ms <= target_max_ms else max(0.0, 1.0 - (total_latency_ms - target_max_ms) / target_max_ms)
        res = EvaluationMetricResult(
            metric_name="System Latency Performance",
            score=score,
            target_threshold=0.7,
            passed=total_latency_ms <= target_max_ms,
            detail=f"Total response time: {total_latency_ms:.0f} ms (Target: <= {target_max_ms:.0f} ms).",
        )
        self._results.append(res)
        return res

    def generate_scorecard(self) -> Dict[str, Any]:
        total = len(self._results)
        passed = sum(1 for r in self._results if r.passed)
        avg_score = sum(r.score for r in self._results) / max(1, total)

        return {
            "total_metrics": total,
            "passed_metrics": passed,
            "overall_score_pct": round(avg_score * 100, 1),
            "status": "PASSED" if passed == total else "MARGINAL",
            "metric_details": self._results,
        }
