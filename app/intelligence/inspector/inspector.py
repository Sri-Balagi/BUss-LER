"""
Time-Travel Debugging & Explainability Runtime Inspector for BizOS.
Captures execution chains, step-by-step playback, state snapshot diffing, and reasoning evidence.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DecisionExplainabilityRecord(BaseModel):
    decision_id: str
    decision_made: str
    confidence_score: float
    evidence_used: List[str] = Field(default_factory=list)
    knowledge_references: List[str] = Field(default_factory=list)
    policy_references: List[str] = Field(default_factory=list)
    alternative_actions_considered: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExecutionStepSnapshot(BaseModel):
    step_index: int
    step_name: str
    component: str # e.g. Planner, Agent, Connector, Memory, Twin
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    state_before: Dict[str, Any] = Field(default_factory=dict)
    state_after: Dict[str, Any] = Field(default_factory=dict)
    explainability: Optional[DecisionExplainabilityRecord] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExecutionTrace(BaseModel):
    trace_id: str
    goal_id: str
    workflow_id: Optional[str] = None
    tenant_id: str = "default"
    execution_mode: str = "PRODUCTION"
    status: str = "COMPLETED"
    steps: List[ExecutionStepSnapshot] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TimeTravelInspector:
    """
    Time-Travel Debugging & Explainability Engine.
    Supports step-by-step playback, pause/resume, snapshot inspection, and execution comparison.
    """

    def __init__(self) -> None:
        self._traces: Dict[str, ExecutionTrace] = {}

    def record_trace(self, trace: ExecutionTrace) -> None:
        self._traces[trace.trace_id] = trace

    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        return self._traces.get(trace_id)

    def replay_step_by_step(self, trace_id: str) -> List[Dict[str, Any]]:
        """Yields sequential execution snapshots for time-travel playback."""
        trace = self.get_trace(trace_id)
        if not trace:
            return []

        playback = []
        for s in trace.steps:
            item = {
                "step_index": s.step_index,
                "step_name": s.step_name,
                "component": s.component,
                "diff": {
                    "before": s.state_before,
                    "after": s.state_after,
                },
                "explainability": s.explainability.model_dump() if s.explainability else None,
            }
            playback.append(item)
        return playback

    def compare_executions(self, trace_id_1: str, trace_id_2: str) -> Dict[str, Any]:
        """Compares two execution runs for regression testing & debugging."""
        t1 = self.get_trace(trace_id_1)
        t2 = self.get_trace(trace_id_2)
        
        if not t1 or not t2:
            return {"error": "One or both traces not found"}

        return {
            "trace_1": {"id": t1.trace_id, "steps_count": len(t1.steps), "mode": t1.execution_mode},
            "trace_2": {"id": t2.trace_id, "steps_count": len(t2.steps), "mode": t2.execution_mode},
            "step_count_diff": len(t1.steps) - len(t2.steps),
        }
