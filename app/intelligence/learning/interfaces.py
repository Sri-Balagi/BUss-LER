from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.intelligence.oversight.cycle.models import CognitiveCycleState
from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.learning.reflection.models import ReflectionReport
from app.intelligence.learning.evaluation.models import OutcomeEvaluation
from app.intelligence.learning.synthesis.models import KnowledgeArtifact
from app.intelligence.learning.repository.models import KnowledgeRepositoryState
from app.intelligence.learning.heuristics.models import Heuristic, HeuristicCatalog

class IReflectionEngine(ABC):
    @abstractmethod
    def generate_reflection(self, cycle_state: CognitiveCycleState) -> ReflectionReport:
        pass

class IOutcomeEvaluationEngine(ABC):
    @abstractmethod
    def evaluate_plan(self, plan: ExecutivePlan, actual_results: Dict[str, float]) -> OutcomeEvaluation:
        pass

class IKnowledgeSynthesisEngine(ABC):
    @abstractmethod
    def synthesize(self, reflection: ReflectionReport, evaluation: OutcomeEvaluation) -> List[KnowledgeArtifact]:
        pass

class IExecutiveKnowledgeRepository(ABC):
    @abstractmethod
    def store_artifact(self, artifact: KnowledgeArtifact) -> None:
        pass
        
    @abstractmethod
    def retrieve_artifacts(self) -> List[KnowledgeArtifact]:
        pass
        
    @abstractmethod
    def get_state(self) -> KnowledgeRepositoryState:
        pass

class IExecutiveHeuristicsEngine(ABC):
    @abstractmethod
    def derive_heuristics(self, artifact: KnowledgeArtifact) -> List[Heuristic]:
        pass
        
    @abstractmethod
    def get_catalog(self) -> HeuristicCatalog:
        pass
