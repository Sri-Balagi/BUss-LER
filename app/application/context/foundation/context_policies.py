"""Context Policies — Milestone 4.

ContextPolicy defines the composition rules for an EnterpriseContext assembly:
  - Which providers to invoke
  - Which providers are required vs optional
  - Token budget
  - Ranking/compression/window-builder strategy identifiers
  - Per-provider collection limits

Factory methods provide pre-configured policies for common use cases.
Future milestones extend policies rather than modifying ContextEngine.
"""

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import ContextSource

# Default token budget matches Gemini 2.5 Flash context window
_DEFAULT_TOKEN_BUDGET = 128_000
_PLANNING_TOKEN_BUDGET = 64_000
_RECOMMENDATION_TOKEN_BUDGET = 32_000


class ContextPolicy(DomainBaseModel):
    """Defines how EnterpriseContext should be assembled.

    Policies are the primary control surface for the ContextEngine.
    The engine never hard-codes assembly logic — all decisions flow through policy.
    """

    policy_id: str
    description: str = ""

    # --- Provider selection ---
    enabled_providers: list[ContextSource]
    required_providers: list[ContextSource] = []
    optional_providers: list[ContextSource] = []

    # --- Token budget ---
    token_budget: int = _DEFAULT_TOKEN_BUDGET

    # --- Strategy selection (string keys looked up in DI registry) ---
    ranker_type: str = "default"
    compressor_type: str = "default"
    window_builder_type: str = "default"

    # --- Reserve Configuration ---
    critical_reserve: float = 0.1

    # --- Per-provider limits ---
    max_memories: int = 10
    max_goals: int = 20
    max_plans: int = 5
    max_recommendations: int = 5
    max_conversation_turns: int = 20
    max_traces: int = 5
    include_traces: bool = True

    @classmethod
    def planning(cls) -> "ContextPolicy":
        """Policy optimized for PlanningEngine consumption."""
        return cls(
            policy_id="planning",
            description="Optimized context assembly for plan generation.",
            enabled_providers=[
                ContextSource.INTENT,
                ContextSource.GOAL,
                ContextSource.MEMORY,
                ContextSource.PLAN,
                ContextSource.TWIN,
                ContextSource.BUSINESS_STATE,
            ],
            required_providers=[ContextSource.GOAL],
            optional_providers=[
                ContextSource.INTENT,
                ContextSource.MEMORY,
                ContextSource.PLAN,
                ContextSource.TWIN,
                ContextSource.BUSINESS_STATE,
            ],
            token_budget=_PLANNING_TOKEN_BUDGET,
            max_memories=8,
            max_goals=15,
            max_plans=3,
            include_traces=False,
            critical_reserve=0.3,
        )

    @classmethod
    def recommendation(cls) -> "ContextPolicy":
        """Policy optimized for RecommendationEngine consumption."""
        return cls(
            policy_id="recommendation",
            description="Optimized context assembly for recommendation generation.",
            enabled_providers=[
                ContextSource.INTENT,
                ContextSource.GOAL,
                ContextSource.MEMORY,
                ContextSource.RECOMMENDATION,
                ContextSource.TWIN,
                ContextSource.BUSINESS_STATE,
            ],
            required_providers=[],
            optional_providers=[
                ContextSource.INTENT,
                ContextSource.GOAL,
                ContextSource.MEMORY,
                ContextSource.RECOMMENDATION,
                ContextSource.TWIN,
                ContextSource.BUSINESS_STATE,
            ],
            token_budget=_RECOMMENDATION_TOKEN_BUDGET,
            max_memories=5,
            max_goals=10,
            max_recommendations=3,
            include_traces=False,
            critical_reserve=0.1,
        )

    @classmethod
    def simulation(cls) -> "ContextPolicy":
        """Placeholder policy for M6 Simulation Engine."""
        return cls(
            policy_id="simulation",
            description="Full context assembly for simulation workflows. (M6 placeholder)",
            enabled_providers=list(ContextSource),
            required_providers=[ContextSource.GOAL, ContextSource.TWIN],
            optional_providers=[
                s
                for s in ContextSource
                if s not in [ContextSource.GOAL, ContextSource.TWIN]
            ],
            token_budget=_DEFAULT_TOKEN_BUDGET,
        )

    @classmethod
    def agent(cls) -> "ContextPolicy":
        """Placeholder policy for M5 Agent Framework."""
        return cls(
            policy_id="agent",
            description="Full context assembly for agent workflows. (M5 placeholder)",
            enabled_providers=list(ContextSource),
            required_providers=[ContextSource.INTENT, ContextSource.GOAL],
            optional_providers=[
                s
                for s in ContextSource
                if s not in [ContextSource.INTENT, ContextSource.GOAL]
            ],
            token_budget=_DEFAULT_TOKEN_BUDGET,
        )

    @classmethod
    def full(cls) -> "ContextPolicy":
        """All providers, maximum budget — for debugging and certification."""
        return cls(
            policy_id="full",
            description="All providers, maximum budget.",
            enabled_providers=list(ContextSource),
            required_providers=[],
            optional_providers=list(ContextSource),
            token_budget=_DEFAULT_TOKEN_BUDGET,
        )


# =============================================================================
# Policy Registry (simple dict — DI layer populates it)
# =============================================================================

BUILT_IN_POLICIES: dict[str, ContextPolicy] = {
    "planning": ContextPolicy.planning(),
    "recommendation": ContextPolicy.recommendation(),
    "simulation": ContextPolicy.simulation(),
    "agent": ContextPolicy.agent(),
    "full": ContextPolicy.full(),
}
