from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum, auto
from uuid import UUID

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
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Output payload from the capability.")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics.")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings encountered.")
    errors: List[str] = Field(default_factory=list, description="Fatal errors encountered.")
    execution_time_ms: int = Field(default=0, description="Total execution time in milliseconds.")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="Resource consumption (e.g., tokens, bytes).")
    retry_count: int = Field(default=0, description="Number of retries attempted.")
    execution_trace_id: Optional[UUID] = Field(default=None, description="Trace ID linking request to result.")
    adapter_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata from the underlying resource adapter (e.g., HTTP status).")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Results from middleware validation.")
