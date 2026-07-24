import enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(enum.StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class JobRecord(BaseModel):
    """Represents a long-running asynchronous job."""
    job_id: str = Field(..., description="Unique job identifier")
    app_id: str = Field(..., description="The ID of the application running the job")
    status: JobStatus = Field(default=JobStatus.PENDING)
    context_data: dict[str, Any] = Field(default_factory=dict, description="Serialized WorkerContext")
    result: dict[str, Any] | None = Field(default=None, description="Job output if completed")
    error: str | None = Field(default=None, description="Error message if failed")
    created_at: float = Field(default_factory=lambda: __import__("time").time())
    updated_at: float = Field(default_factory=lambda: __import__("time").time())
