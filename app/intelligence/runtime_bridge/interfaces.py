from abc import ABC, abstractmethod
from typing import List

from app.intelligence.decision.planning.models import ExecutiveDirective
from app.intelligence.runtime_bridge.models import ExecutionSummary, RuntimeIntegrationResult


class ISupervisorAdapter(ABC):
    @abstractmethod
    def dispatch_directive(self, directive: ExecutiveDirective) -> str:
        """Returns a runtime task/dag handle."""
        pass

    @abstractmethod
    def get_execution_summary(self, handle: str) -> ExecutionSummary:
        """Retrieves execution state for a given handle."""
        pass

class IIntelligenceRuntimeBridge(ABC):
    @abstractmethod
    def execute_directives(self, directives: list[ExecutiveDirective]) -> RuntimeIntegrationResult:
        pass
