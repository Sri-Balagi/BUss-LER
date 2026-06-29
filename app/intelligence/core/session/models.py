from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ReasoningMode(str, Enum):
    """Declarative reasoning modes that affect controller behavior."""
    FAST = "FAST"
    ANALYTICAL = "ANALYTICAL"
    EXPLORATORY = "EXPLORATORY"
    CONSERVATIVE = "CONSERVATIVE"
    EMERGENCY = "EMERGENCY"
    CREATIVE = "CREATIVE"

class CognitiveMetrics(BaseModel):
    """Passive observability metrics for a cognitive session."""
    iteration_count: int = 0
    convergence_duration_ms: int = 0
    planning_latency_ms: int = 0
    discarded_hypotheses: int = 0
    branching_factor: float = 0.0
    confidence_progression: list[float] = Field(default_factory=list)
    uncertainty_progression: list[float] = Field(default_factory=list)
    simulation_count: int = 0

class SessionBudget(BaseModel):
    """Budget constraints for a cognitive session."""
    max_iterations: int = 10
    max_duration_ms: int = 60000
    max_llm_tokens: Optional[int] = None
    max_simulations: int = 5

class TerminationPolicy(BaseModel):
    """Rules defining when a cognitive loop should break."""
    target_confidence: float = 0.85
    max_uncertainty: float = 0.3
    require_stable_assumptions: bool = True
    enforce_strict_budget: bool = True
