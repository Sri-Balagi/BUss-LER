from enum import Enum, auto
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExecutionStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    TIMEOUT = auto()
    CANCELLED = auto()


class CapabilityResult(BaseModel):
    """
    Standardized runtime artifact representing the outcome of a capability execution.
    """

    status: ExecutionStatus = Field(..., description="Final execution status.")
    outputs: dict[str, Any] = Field(
        default_factory=dict, description="Output payload from the capability."
    )
    metrics: dict[str, Any] = Field(default_factory=dict, description="Execution metrics.")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings encountered.")
    errors: list[str] = Field(default_factory=list, description="Fatal errors encountered.")
    execution_time_ms: int = Field(default=0, description="Total execution time in milliseconds.")
    resource_usage: dict[str, Any] = Field(
        default_factory=dict, description="Resource consumption (e.g., tokens, bytes)."
    )
    retry_count: int = Field(default=0, description="Number of retries attempted.")
    execution_trace_id: UUID | None = Field(
        default=None, description="Trace ID linking request to result."
    )
    adapter_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from the underlying resource adapter (e.g., HTTP status).",
    )
    validation_results: dict[str, Any] = Field(
        default_factory=dict, description="Results from middleware validation."
    )
