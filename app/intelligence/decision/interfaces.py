from abc import ABC, abstractmethod
from typing import List, Optional

from app.intelligence.intake.situation.models import SituationAssessment
from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.strategy.constraints.models import StrategicConstraintSet
from app.intelligence.strategy.policy.models import PolicyAssessment

from app.intelligence.decision.decision.models import ExecutiveDecision, DecisionAlternative
from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.decision.simulation.models import SimulationResult, SimulationScenario
from app.intelligence.decision.uncertainty.models import UncertaintyAssessment
from app.intelligence.decision.confidence.models import ConfidenceAssessment

class IDecisionEngine(ABC):
    @abstractmethod
    def evaluate(self, 
                 objective: ExecutiveObjective, 
                 situation: SituationAssessment, 
                 constraints: StrategicConstraintSet, 
                 policy: PolicyAssessment,
                 alternatives: List[DecisionAlternative]) -> Optional[ExecutiveDecision]:
        pass

class IPlanningEngine(ABC):
    @abstractmethod
    def generate_plan(self, decision: ExecutiveDecision) -> ExecutivePlan:
        pass

class ISimulationEngine(ABC):
    @abstractmethod
    def simulate(self, plan: ExecutivePlan, scenarios: List[SimulationScenario]) -> List[SimulationResult]:
        pass

class IUncertaintyEngine(ABC):
    @abstractmethod
    def estimate_uncertainty(self) -> UncertaintyAssessment:
        pass

class IConfidenceEngine(ABC):
    @abstractmethod
    def evaluate_confidence(self, uncertainty: UncertaintyAssessment) -> ConfidenceAssessment:
        pass
