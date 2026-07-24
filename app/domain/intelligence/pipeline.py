import abc
from typing import TypeVar

from pydantic import BaseModel

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.telemetry import IntelligenceMetrics

T_Input = TypeVar('T_Input')
T_Output = TypeVar('T_Output')


class PipelineContext[T_Input](BaseModel):
    """Wraps the IntelligenceContext securely for pipeline execution."""
    execution_context: IntelligenceContext
    payload: T_Input

    class Config:
        arbitrary_types_allowed = True


class PipelineResult[T_Output](BaseModel):
    """Standardized output for all pipeline executions."""
    context: IntelligenceContext
    payload: T_Output | None = None
    metrics: IntelligenceMetrics
    is_success: bool = True
    error_message: str | None = None

    class Config:
        arbitrary_types_allowed = True


class IPipelineStep[T_Input, T_Output](abc.ABC):
    """A discrete, reusable operation inside an intelligence pipeline."""

    @abc.abstractmethod
    async def execute(self, context: PipelineContext[T_Input]) -> PipelineResult[T_Output]:
        pass


class IIntelligencePipeline[T_Input, T_Output](abc.ABC):
    """The canonical interface for composed intelligence execution (e.g., RetrievalPipeline)."""

    @abc.abstractmethod
    async def execute(self, context: PipelineContext[T_Input]) -> PipelineResult[T_Output]:
        pass
