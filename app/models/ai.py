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


class ClassifyRequest(DomainBaseModel):
    """Domain model for requesting structured AI classification.

    Used exclusively by AIKernel.classify().
    The AI must return a structured JSON response validated against a Pydantic schema.
    Free-form text responses are prohibited.
    """
    prompt_id: str = Field(..., description="The versioned prompt ID for classification.")
    version: str = Field(default="v1", description="The prompt version.")
    content: str = Field(..., description="The raw text content to classify.")
    context: dict = Field(
        default_factory=dict,
        description="Additional context variables for prompt interpolation.",
    )
    system_instruction: Optional[str] = Field(
        None,
        description="Optional system-level instructions for the classification task.",
    )


class ClassifyResponse(DomainBaseModel):
    """Domain model for structured AI classification responses.

    The raw_json field contains the validated JSON extracted from the AI response.
    Services must validate raw_json against their expected Pydantic schema before use.

    Validation pipeline enforced by callers:
        ClassifyResponse.raw_json → Pydantic schema → domain object → persistence
    """
    raw_json: dict = Field(
        ...,
        description=(
            "Validated JSON payload from the AI provider. "
            "Must be validated by the caller against the expected domain schema."
        ),
    )
    metadata: AIResponseMetadata = Field(..., description="Provider and execution metadata.")

