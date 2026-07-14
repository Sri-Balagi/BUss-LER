from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from app.intelligence.core.session.session import CognitiveSession


class PipelinePhase(StrEnum):
    """The ordered phases of the continuous cognitive loop."""
    
    OBSERVE = "OBSERVE"
    UNDERSTAND = "UNDERSTAND"
    REASON = "REASON"
    PLAN = "PLAN"
    DELEGATE = "DELEGATE"
    EXECUTE = "EXECUTE"
    REFLECT = "REFLECT"
    LEARN = "LEARN"


class PhaseResultStatus(StrEnum):
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    YIELDED = "YIELDED"  # Used when the phase needs to pause for external input (e.g., human approval)


class PhaseResult(BaseModel):
    """Immutable output of a single pipeline phase execution."""
    
    phase: PipelinePhase
    status: PhaseResultStatus
    artifact: Any = None
    error_message: str | None = None
    duration_ms: float = 0.0


class IPhase(ABC):
    """Interface for a discrete step in the cognitive loop."""
    
    @property
    @abstractmethod
    def phase_type(self) -> PipelinePhase:
        pass
        
    @abstractmethod
    async def execute(self, session: CognitiveSession) -> PhaseResult:
        """Execute the phase logic, returning an immutable PhaseResult."""
        pass
