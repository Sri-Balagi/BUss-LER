from abc import ABC, abstractmethod

from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.integration.models import ExecutiveIntelligenceResult


class ICognitivePipeline(ABC):
    @abstractmethod
    def run_pipeline(
        self, raw_request: str, session: CognitiveSession
    ) -> ExecutiveIntelligenceResult:
        pass


class IExecutiveIntelligenceOrchestrator(ABC):
    @abstractmethod
    def process_request(self, raw_request: str) -> ExecutiveIntelligenceResult:
        pass
