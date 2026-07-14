from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.intelligence.core.session.models import ReasoningMode
from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.integration.models import ExecutiveIntelligenceResult


class IExecutiveController(ABC):
    """The central lifecycle orchestrator for the Autonomous Intelligence loop."""

    @abstractmethod
    async def process_request(
        self,
        raw_request: str,
        twin_id: UUID | None = None,
        mode: ReasoningMode = ReasoningMode.ANALYTICAL,
    ) -> ExecutiveIntelligenceResult:
        """Start a new autonomous cognitive loop from a raw user request.
        
        This method wraps the entire session lifecycle for a given request.
        For M7, it preserves backward compatibility with the Wave-0 orchestrator
        return type, while introducing the rich CognitiveSession internally.
        """
        pass

    @abstractmethod
    async def resume_session(
        self, session_id: str, trigger_event: Any = None
    ) -> ExecutiveIntelligenceResult:
        """Resume a suspended cognitive session.
        
        Called automatically by the EventBus when external events (e.g., Goal Updated)
        occur, or manually via an API endpoint.
        """
        pass
