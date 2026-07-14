from enum import StrEnum

from pydantic import BaseModel, Field

from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import ExecutiveDirective, ExecutivePlan
from app.intelligence.intake.intent.models import ExecutiveIntent
from app.intelligence.intake.situation.models import SituationAssessment
from app.intelligence.learning.heuristics.models import Heuristic
from app.intelligence.learning.reflection.models import ReflectionReport
from app.intelligence.learning.synthesis.models import KnowledgeArtifact
from app.intelligence.oversight.convergence.models import ConvergenceAssessment
from app.intelligence.oversight.validation.models import ValidationAssessment
from app.intelligence.strategy.objectives.models import ExecutiveObjective


class CognitivePipelineState(StrEnum):
    INITIALIZED = "INITIALIZED"
    OBSERVING = "OBSERVING"
    STRATEGIZING = "STRATEGIZING"
    DECIDING = "DECIDING"
    OVERSIGHT = "OVERSIGHT"
    LEARNING = "LEARNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PipelineMetrics(BaseModel):
    duration_ms: float = 0.0
    iterations: int = 0
    artifacts_produced: int = 0


class IntegrationSummary(BaseModel):
    state: CognitivePipelineState
    metrics: PipelineMetrics
    warnings: list[str] = Field(default_factory=list)


class ExecutiveIntelligenceResult(BaseModel):
    """The unified output of an entire intelligence cycle."""

    session_id: str
    summary: IntegrationSummary

    # Artifacts aggregated from the pipeline
    intent: ExecutiveIntent | None = None
    situation: SituationAssessment | None = None
    objectives: list[ExecutiveObjective] = Field(default_factory=list)
    decision: ExecutiveDecision | None = None
    plan: ExecutivePlan | None = None
    directive: ExecutiveDirective | None = None
    convergence: ConvergenceAssessment | None = None
    validation: ValidationAssessment | None = None
    reflection: ReflectionReport | None = None
    knowledge_artifacts: list[KnowledgeArtifact] = Field(default_factory=list)
    heuristics: list[Heuristic] = Field(default_factory=list)
