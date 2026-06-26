from typing import Any, Dict, Optional
from app.models.schemas import DomainBaseModel
from pydantic import Field

class AIResponseMetadata(DomainBaseModel):
    """Metadata attached to an AI response."""
    provider: str
    model: str
    latency_ms: float
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    finish_reason: Optional[str] = None


class AIRequest(DomainBaseModel):
    """Domain model for requesting AI text generation."""
    prompt_id: str = Field(..., description="The unique identifier for the versioned prompt.")
    version: str = Field(default="v1", description="The prompt version.")
    context: Dict[str, Any] = Field(default_factory=dict, description="Variables to interpolate into the prompt template.")
    system_instruction: Optional[str] = Field(None, description="Optional system-level instructions.")


class AIResponse(DomainBaseModel):
    """Domain model for AI text generation responses."""
    content: str = Field(..., description="The generated text.")
    metadata: AIResponseMetadata = Field(..., description="Provider and execution metadata.")


class EmbeddingRequest(DomainBaseModel):
    """Domain model for requesting AI vector embeddings."""
    text: str = Field(..., description="The content to embed.")
    model: Optional[str] = Field(None, description="Specific model to use (if overriding default).")


class EmbeddingResponse(DomainBaseModel):
    """Domain model for AI vector embedding responses."""
    vector: list[float] = Field(..., description="High-dimensional embedding vector.")
    metadata: AIResponseMetadata = Field(..., description="Provider and execution metadata.")
