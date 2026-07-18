from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ApplicationContext(BaseModel):
    """Base context for executing a cognitive application."""
    user_id: str = Field(..., description="The user initiating the request")
    tenant_id: str = Field(..., description="The tenant context")
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    span_id: Optional[str] = Field(None, description="Distributed tracing span ID")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Temporary variables for execution")

class ChatContext(ApplicationContext):
    """Context specifically for conversational copilots."""
    session_id: str = Field(..., description="Chat session ID")
    # Additional chat specific state

class WorkerContext(ApplicationContext):
    """Context specifically for autonomous workers."""
    workflow_id: str = Field(..., description="The workflow execution ID")
    task_id: str = Field(..., description="The specific task ID")
