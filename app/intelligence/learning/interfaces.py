from abc import ABC, abstractmethod

from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.learning.evaluation.models import OutcomeEvaluation
from app.intelligence.learning.heuristics.models import Heuristic, HeuristicCatalog
from app.intelligence.learning.reflection.models import ReflectionReport
from app.intelligence.learning.repository.models import KnowledgeRepositoryState
from app.intelligence.learning.synthesis.models import KnowledgeArtifact
from app.intelligence.oversight.cycle.models import CognitiveCycleState


class IReflectionEngine(ABC):
    @abstractmethod
    def generate_reflection(self, cycle_state: CognitiveCycleState) -> ReflectionReport:
        pass


class IOutcomeEvaluationEngine(ABC):
    @abstractmethod
    def evaluate_plan(
        self, plan: ExecutivePlan, actual_results: dict[str, float]
    ) -> OutcomeEvaluation:
        pass


class IKnowledgeSynthesisEngine(ABC):
    @abstractmethod
    def synthesize(
        self, reflection: ReflectionReport, evaluation: OutcomeEvaluation
    ) -> list[KnowledgeArtifact]:
        pass


class IExecutiveKnowledgeRepository(ABC):
    @abstractmethod
    def store_artifact(self, artifact: KnowledgeArtifact) -> None:
        pass

    @abstractmethod
    def retrieve_artifacts(self) -> list[KnowledgeArtifact]:
        pass

    @abstractmethod
    def get_state(self) -> KnowledgeRepositoryState:
        pass


class IExecutiveHeuristicsEngine(ABC):
    @abstractmethod
    def derive_heuristics(self, artifact: KnowledgeArtifact) -> list[Heuristic]:
        pass

    @abstractmethod
    def get_catalog(self) -> HeuristicCatalog:
        pass
