from pydantic import BaseModel, Field


class CapabilityPolicy(BaseModel):
    """
    Declarative execution constraints for capabilities.
    """
    max_retries: int = Field(default=3, description="Maximum number of retries allowed.")
    timeout_ms: int = Field(default=30000, description="Execution timeout in milliseconds.")
    idempotent: bool = Field(default=False, description="Whether the operation is safe to retry blindly.")
    rate_limit_per_minute: int | None = Field(default=None, description="Maximum executions per minute.")
    requires_audit: bool = Field(default=False, description="Whether the execution requires audit logging.")
