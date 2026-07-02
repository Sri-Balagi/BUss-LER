from abc import ABC, abstractmethod

from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.oversight.arbitration.models import ArbitrationDecision
from app.intelligence.oversight.assumptions.models import Assumption, AssumptionRegistry
from app.intelligence.oversight.convergence.models import ConvergenceAssessment
from app.intelligence.oversight.cycle.models import CognitiveCycleState
from app.intelligence.oversight.validation.models import ValidationAssessment


class ICognitiveCycleController(ABC):
    @abstractmethod
    def initialize_cycle(self, max_iterations: int = 5) -> CognitiveCycleState:
        pass

    @abstractmethod
    def advance_iteration(self, state: CognitiveCycleState) -> CognitiveCycleState:
        pass

    @abstractmethod
    def mark_converged(self, state: CognitiveCycleState) -> CognitiveCycleState:
        pass


class IConvergenceEngine(ABC):
    @abstractmethod
    def evaluate_convergence(
        self, historical_decisions: list[ExecutiveDecision], current_decision: ExecutiveDecision
    ) -> ConvergenceAssessment:
        pass


class IExecutiveArbitrationEngine(ABC):
    @abstractmethod
    def arbitrate_decisions(self, decisions: list[ExecutiveDecision]) -> ArbitrationDecision:
        pass


class IAssumptionManager(ABC):
    @abstractmethod
    def add_assumption(self, description: str) -> Assumption:
        pass

    @abstractmethod
    def invalidate_assumption(self, assumption_id: str) -> bool:
        pass

    @abstractmethod
    def get_registry(self) -> AssumptionRegistry:
        pass


class IExecutiveValidationEngine(ABC):
    @abstractmethod
    def validate_decision(self, decision: ExecutiveDecision) -> ValidationAssessment:
        pass

    @abstractmethod
    def validate_plan(self, plan: ExecutivePlan) -> ValidationAssessment:
        pass
