from typing import Any

from pydantic import BaseModel, Field

from app.domain.intelligence.context import IntelligenceContext


class ReasoningContext(IntelligenceContext):
    """
    Extends the canonical IntelligenceContext with reasoning-specific metadata
    such as grounding variables or inference constraints.
    """
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    stop_sequences: list[str] = Field(default_factory=list)
    # The active digital twin state should be passed separately to the pipeline,
    # or injected into the execution payload.


class ReasoningQuery(BaseModel):
    """Canonical model for a structured reasoning request."""
    query_text: str = Field(..., description="The primary instruction or question.")
    system_prompt_override: str | None = Field(default=None)
    required_schema: dict[str, Any] | None = Field(default=None, description="Optional JSON schema for structured output.")
    context_data: dict[str, Any] = Field(default_factory=dict, description="Extraneous data outside the Twin needed for this reasoning step.")


class ReasoningResponse(BaseModel):
    """Canonical reasoning result."""
    payload: Any = Field(..., description="The parsed output from the provider (string or dict).")
    confidence: float = Field(default=1.0, description="Confidence score [0.0 - 1.0].")
    evidence: list[str] = Field(default_factory=list, description="Citations or logical steps used to derive the answer.")
    reasoning_trace: str | None = Field(default=None, description="Detailed trace or Chain of Thought if provided.")
    execution_metadata: dict[str, Any] = Field(default_factory=dict, description="Timings, tokens used, etc.")
    provider_metadata: dict[str, Any] = Field(default_factory=dict, description="Provider specific metadata (e.g., model version, finish reason).")
