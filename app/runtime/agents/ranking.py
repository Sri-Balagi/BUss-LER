from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from app.runtime.agents.health import AgentHealth
from app.runtime.agents.specification import AgentSpecification

if TYPE_CHECKING:
    from app.runtime.agents.registry import ResolutionContext


class RankingScore(BaseModel):
    """
    Structured outcome of a ranking evaluation.
    Used for Registry comparison and observational telemetry.
    """

    overall_score: float = Field(default=0.0)
    health_contribution: float = Field(default=0.0)
    cost_contribution: float = Field(default=0.0)
    latency_contribution: float = Field(default=0.0)
    availability_contribution: float = Field(default=0.0)

    def __lt__(self, other):
        return self.overall_score < other.overall_score


class IRankingStrategy(ABC):
    """
    Abstract strategy for scoring capability candidates.
    Allows decoupling of resolution logic from heuristics.
    """

    @abstractmethod
    def score(
        self, spec: AgentSpecification, health: AgentHealth, context: "ResolutionContext"
    ) -> RankingScore:
        pass


class HealthRankingStrategy(IRankingStrategy):
    """Scores based on advisory health telemetry."""

    def score(
        self, spec: AgentSpecification, health: AgentHealth, context: "ResolutionContext"
    ) -> RankingScore:
        if not health.is_available or health.in_cooldown:
            return RankingScore(overall_score=0.0, availability_contribution=0.0)

        # Base score on success rate. (0.0 to 1.0)
        health_score = health.success_rate
        # Example penalty for recent failures
        penalty = health.recent_failures * 0.1
        final_score = max(0.0, health_score - penalty)

        return RankingScore(
            overall_score=final_score,
            health_contribution=final_score,
            availability_contribution=1.0 if health.is_available else 0.0,
        )


class CostRankingStrategy(IRankingStrategy):
    """Placeholder strategy demonstrating extensibility."""

    def score(
        self, spec: AgentSpecification, health: AgentHealth, context: "ResolutionContext"
    ) -> RankingScore:
        # In a real system, cost limits would be checked.
        return RankingScore(overall_score=1.0, cost_contribution=1.0)


class CompositeRankingStrategy(IRankingStrategy):
    """Combines multiple strategies."""

    def __init__(self, strategies: list[IRankingStrategy]):
        self._strategies = strategies

    def score(
        self, spec: AgentSpecification, health: AgentHealth, context: "ResolutionContext"
    ) -> RankingScore:
        composite = RankingScore()
        for strategy in self._strategies:
            s = strategy.score(spec, health, context)
            composite.overall_score += s.overall_score
            composite.health_contribution += s.health_contribution
            composite.cost_contribution += s.cost_contribution
            composite.latency_contribution += s.latency_contribution
            composite.availability_contribution += s.availability_contribution

        # Optional: Normalize by count
        if self._strategies:
            composite.overall_score /= len(self._strategies)

        return composite
