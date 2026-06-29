from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

from app.intelligence.intake.intent.models import ExecutiveIntent
from app.intelligence.intake.situation.models import SituationAssessment
from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import ExecutivePlan, ExecutiveDirective
from app.intelligence.oversight.convergence.models import ConvergenceAssessment
from app.intelligence.oversight.validation.models import ValidationAssessment
from app.intelligence.learning.reflection.models import ReflectionReport
from app.intelligence.learning.synthesis.models import KnowledgeArtifact
from app.intelligence.learning.heuristics.models import Heuristic

class CognitivePipelineState(str, Enum):
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
    warnings: List[str] = Field(default_factory=list)

class ExecutiveIntelligenceResult(BaseModel):
    """The unified output of an entire intelligence cycle."""
    session_id: str
    summary: IntegrationSummary
    
    # Artifacts aggregated from the pipeline
    intent: Optional[ExecutiveIntent] = None
    situation: Optional[SituationAssessment] = None
    objectives: List[ExecutiveObjective] = Field(default_factory=list)
    decision: Optional[ExecutiveDecision] = None
    plan: Optional[ExecutivePlan] = None
    directive: Optional[ExecutiveDirective] = None
    convergence: Optional[ConvergenceAssessment] = None
    validation: Optional[ValidationAssessment] = None
    reflection: Optional[ReflectionReport] = None
    knowledge_artifacts: List[KnowledgeArtifact] = Field(default_factory=list)
    heuristics: List[Heuristic] = Field(default_factory=list)
