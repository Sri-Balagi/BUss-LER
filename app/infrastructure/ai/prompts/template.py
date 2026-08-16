"""Models for Prompt Registry and Templating."""

from pydantic import ConfigDict, Field

from app.interfaces.http.schemas.base import DomainBaseModel


class ProviderVariant(DomainBaseModel):
    """A provider-specific variant of a prompt template."""

    provider_name: str = Field(
        ...,
        description="The name of the provider this variant targets (e.g., 'anthropic', 'openai')",
    )
    template: str = Field(
        ..., description="The template string optimized for this specific provider"
    )
    # Allows storing things like model-specific temperature preferences if needed in the future
    metadata: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)


class PromptTemplate(DomainBaseModel):
    """A versioned, provider-aware prompt template.

    Part of the R3 Prompt Registry evolution, this model supports:
    - Base template string with {variable} interpolation
    - Declared context variables for validation at resolution time
    - Provider-specific variants (e.g. Claude-optimized vs Gemini-optimized)
    - Metadata for categorisation and tracking
    """

    prompt_id: str = Field(
        ..., description="Unique identifier for this prompt (e.g. 'intent_classification')"
    )
    version: str = Field(
        ..., description="Semantic version or version string (e.g. 'v1', 'v1.1.0')"
    )
    base_template: str = Field(
        ..., description="The default template string to use if no provider variant matches"
    )
    context_variables: list[str] = Field(
        default_factory=list,
        description="List of variables that must be provided in context during resolution",
    )
    provider_variants: list[ProviderVariant] = Field(
        default_factory=list, description="Optional provider-specific overrides for this template"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional metadata (author, capability area, etc.)"
    )

    model_config = ConfigDict(frozen=True)
