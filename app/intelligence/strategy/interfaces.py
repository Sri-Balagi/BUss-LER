from abc import ABC, abstractmethod
from typing import List, Optional

from app.intelligence.intake.intent.models import ExecutiveIntent
from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.strategy.goals.models import GoalCollection, Goal
from app.intelligence.strategy.conflict.models import ConflictAssessment
from app.intelligence.strategy.constraints.models import StrategicConstraintSet
from app.intelligence.strategy.policy.models import PolicyAssessment
from app.intelligence.strategy.library.models import StrategyCatalog, StrategyDefinition
from app.intelligence.strategy.timeline.models import StrategicTimeline

class IExecutiveObjectivesEngine(ABC):
    @abstractmethod
    def create_objective_from_intent(self, intent: ExecutiveIntent) -> ExecutiveObjective:
        pass

class IGoalManagementEngine(ABC):
    @abstractmethod
    def derive_goals(self, objective: ExecutiveObjective) -> GoalCollection:
        pass

class IObjectiveConflictResolver(ABC):
    @abstractmethod
    def detect_conflicts(self, objectives: List[ExecutiveObjective], goals: List[Goal]) -> List[ConflictAssessment]:
        pass

class IStrategicConstraintsEngine(ABC):
    @abstractmethod
    def evaluate_constraints(self) -> StrategicConstraintSet:
        pass

class IBusinessPolicyEngine(ABC):
    @abstractmethod
    def evaluate_objective(self, objective: ExecutiveObjective) -> PolicyAssessment:
        pass

class IStrategyLibrary(ABC):
    @abstractmethod
    def get_catalog(self) -> StrategyCatalog:
        pass
    
class IStrategicTimelineEngine(ABC):
    @abstractmethod
    def generate_timeline(self, objectives: List[ExecutiveObjective]) -> StrategicTimeline:
        pass
