import abc
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.telemetry import IntelligenceMetrics


T_Input = TypeVar('T_Input')
T_Output = TypeVar('T_Output')


class PipelineContext(BaseModel, Generic[T_Input]):
    """Wraps the IntelligenceContext securely for pipeline execution."""
    execution_context: IntelligenceContext
    payload: T_Input
    
    class Config:
        arbitrary_types_allowed = True


class PipelineResult(BaseModel, Generic[T_Output]):
    """Standardized output for all pipeline executions."""
    context: IntelligenceContext
    payload: Optional[T_Output] = None
    metrics: IntelligenceMetrics
    is_success: bool = True
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class IPipelineStep(abc.ABC, Generic[T_Input, T_Output]):
    """A discrete, reusable operation inside an intelligence pipeline."""
    
    @abc.abstractmethod
    async def execute(self, context: PipelineContext[T_Input]) -> PipelineResult[T_Output]:
        pass


class IIntelligencePipeline(abc.ABC, Generic[T_Input, T_Output]):
    """The canonical interface for composed intelligence execution (e.g., RetrievalPipeline)."""
    
    @abc.abstractmethod
    async def execute(self, context: PipelineContext[T_Input]) -> PipelineResult[T_Output]:
        pass
