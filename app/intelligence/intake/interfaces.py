from abc import ABC, abstractmethod

from app.intelligence.intake.intent.models import ExecutiveIntent
from app.intelligence.intake.kpi.models import KPIAssessment
from app.intelligence.intake.situation.models import SituationAssessment
from app.intelligence.workspaces.world_model.world_model import BusinessWorldModel


class IIntentEngine(ABC):
    @abstractmethod
    def parse_intent(self, raw_request: str) -> ExecutiveIntent:
        pass


class IKPIEngine(ABC):
    @abstractmethod
    def evaluate_metric(self, kpi_id: str, current: float, target: float) -> KPIAssessment:
        pass


class ISituationAnalysisEngine(ABC):
    @abstractmethod
    def analyze(
        self,
        intent: ExecutiveIntent | None,
        kpis: list[KPIAssessment],
        world_model: BusinessWorldModel,
    ) -> SituationAssessment:
        pass
