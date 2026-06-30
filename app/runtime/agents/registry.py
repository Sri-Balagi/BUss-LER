import time
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from app.runtime.agents.capability import Capability
from app.runtime.agents.interfaces import IAgentFactory
from app.runtime.agents.monitor import AgentHealthMonitor
from app.runtime.agents.permissions import AgentPermission
from app.runtime.agents.ranking import IRankingStrategy, RankingScore
from app.runtime.agents.specification import AgentSpecification


class ResolutionContext(BaseModel):
    """
    Stable input context for Registry resolution.
    Encapsulates all dynamic parameters for capability routing.
    """
    requested_capability: Capability
    execution_scope: str = Field(default="default")
    preferred_version: str | None = Field(default=None)
    required_permissions: set[AgentPermission] = Field(default_factory=set)
    cost_constraints: dict[str, Any] = Field(default_factory=dict)
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)

@dataclass
class ResolutionTrace:
    """Diagnostic trace of the resolution process. Not used for execution logic."""
    evaluated_candidates: int = 0
    rankings: dict[str, RankingScore] = field(default_factory=dict)
    rejected_candidates: list[str] = field(default_factory=list)
    rejection_reasons: dict[str, str] = field(default_factory=dict)
    total_resolution_time_ms: float = 0.0

@dataclass
class ResolutionDecision:
    """Robust outcome of capability resolution."""
    selected_factory: IAgentFactory | None
    selected_specification: AgentSpecification | None
    ranking_score: RankingScore | None
    selection_reason: str
    fallback_candidates: list[AgentSpecification] = field(default_factory=list)
    trace: ResolutionTrace = field(default_factory=ResolutionTrace)

class AgentRegistry:
    """
    The production capability resolution engine.
    Orchestrates lookup and scoring without managing agent state.
    """
    def __init__(self, health_monitor: AgentHealthMonitor, ranking_strategy: IRankingStrategy):
        self._health_monitor = health_monitor
        self._ranking_strategy = ranking_strategy
        self._registry: list[tuple[AgentSpecification, IAgentFactory]] = []

    def register(self, specification: AgentSpecification, factory: IAgentFactory) -> None:
        """Registers a new agent specification and its backing factory."""
        self._registry.append((specification, factory))

    def _matches_capability(self, spec: AgentSpecification, target: Capability) -> bool:
        # Capability objects could have complex rules. For this M5 scope,
        # we assume if the agent's spec declares a capability string matching the id, it's a candidate.
        return target.capability_id in spec.capabilities

    def _has_required_permissions(self, spec: AgentSpecification, required: set[AgentPermission]) -> bool:
        return required.issubset(set(spec.permissions))

    def resolve(self, context: ResolutionContext) -> ResolutionDecision:
        start_time = time.time()
        trace = ResolutionTrace()

        candidates: list[tuple[AgentSpecification, IAgentFactory, RankingScore]] = []

        for spec, factory in self._registry:
            trace.evaluated_candidates += 1

            # Check Capability matching
            if not self._matches_capability(spec, context.requested_capability):
                trace.rejected_candidates.append(spec.identity)
                trace.rejection_reasons[spec.identity] = "Capability mismatch"
                continue

            # Check permissions
            if not self._has_required_permissions(spec, context.required_permissions):
                trace.rejected_candidates.append(spec.identity)
                trace.rejection_reasons[spec.identity] = "Insufficient permissions"
                continue

            # Capability matches. Query health.
            health = self._health_monitor.get_health(spec.identity)

            # Score
            score = self._ranking_strategy.score(spec, health, context)
            trace.rankings[spec.identity] = score

            # Filter zero-scored items if needed (e.g. unavailable)
            if score.overall_score <= 0.0:
                trace.rejected_candidates.append(spec.identity)
                trace.rejection_reasons[spec.identity] = "Score <= 0 (Unavailable or unhealthy)"
                continue

            candidates.append((spec, factory, score))

        trace.total_resolution_time_ms = (time.time() - start_time) * 1000.0

        if not candidates:
            return ResolutionDecision(
                selected_factory=None,
                selected_specification=None,
                ranking_score=None,
                selection_reason="No valid candidates found",
                trace=trace
            )

        # Sort candidates descending by overall score
        candidates.sort(key=lambda item: item[2].overall_score, reverse=True)

        selected_spec, selected_factory, selected_score = candidates[0]
        fallbacks = [c[0] for c in candidates[1:]]

        return ResolutionDecision(
            selected_factory=selected_factory,
            selected_specification=selected_spec,
            ranking_score=selected_score,
            selection_reason="Highest ranking valid candidate",
            fallback_candidates=fallbacks,
            trace=trace
        )
