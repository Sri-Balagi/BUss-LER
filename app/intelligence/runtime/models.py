from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Any

class RuntimeExecutionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RuntimeMetrics(BaseModel):
    execution_time_ms: float = 0.0
    tasks_spawned: int = 0
    capabilities_invoked: int = 0

class DirectiveExecutionMapping(BaseModel):
    directive_id: str
    runtime_task_id: str
    status: RuntimeExecutionStatus

class ExecutionSummary(BaseModel):
    """Summarizes the final state of execution from the Runtime."""
    summary_id: str
    overall_status: RuntimeExecutionStatus
    directive_mappings: List[DirectiveExecutionMapping] = Field(default_factory=list)
    metrics: RuntimeMetrics
    error_message: Optional[str] = None

class RuntimeIntegrationRequest(BaseModel):
    request_id: str
    directives: List[Any]  # Will hold ExecutiveDirective at runtime

class RuntimeIntegrationResult(BaseModel):
    result_id: str
    summary: ExecutionSummary
