"""Structured Telemetry & Observability Metadata Engine for AI Operations."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ExecutionTelemetryRecord:
    """Structured execution metadata record for an AI operation."""

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    goal_id: Optional[str] = None
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    provider: str = "gemini-flash"
    model: str = "gemini-2.5-flash"
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    retry_count: int = 0
    success: bool = True
    error_message: Optional[str] = None

    def calculate_cost(self) -> float:
        """Estimate token cost for Gemini Flash / Pro models."""
        # Gemini 2.5 Flash pricing estimate: $0.075 / 1M prompt, $0.30 / 1M output
        prompt_cost = (self.prompt_tokens / 1_000_000.0) * 0.075
        completion_cost = (self.completion_tokens / 1_000_000.0) * 0.30
        self.estimated_cost_usd = prompt_cost + completion_cost
        return self.estimated_cost_usd


class TelemetryTracker:
    """Central telemetry collector for recording AI execution metrics."""

    def __init__(self):
        self._records: List[ExecutionTelemetryRecord] = []

    def record(self, record: ExecutionTelemetryRecord) -> None:
        record.total_tokens = record.prompt_tokens + record.completion_tokens
        record.calculate_cost()
        self._records.append(record)

        logger.info(
            "AI Execution Telemetry",
            trace_id=record.trace_id,
            provider=record.provider,
            model=record.model,
            latency_ms=round(record.latency_ms, 2),
            prompt_tokens=record.prompt_tokens,
            completion_tokens=record.completion_tokens,
            total_tokens=record.total_tokens,
            cost_usd=f"${record.estimated_cost_usd:.6f}",
        )

    def get_summary(self) -> Dict[str, Any]:
        total_calls = len(self._records)
        total_latency = sum(r.latency_ms for r in self._records)
        total_tokens = sum(r.total_tokens for r in self._records)
        total_cost = sum(r.estimated_cost_usd for r in self._records)
        failed_calls = sum(1 for r in self._records if not r.success)

        return {
            "total_calls": total_calls,
            "avg_latency_ms": round(total_latency / total_calls, 2) if total_calls > 0 else 0.0,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "failed_calls": failed_calls,
        }
