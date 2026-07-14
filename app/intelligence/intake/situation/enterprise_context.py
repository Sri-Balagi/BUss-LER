"""Enterprise Context domain models — Milestone 4.

The EnterpriseContext is the canonical, immutable, versioned cognitive object
consumed by all AI reasoning operations (Planning, Recommendation, Agents, Simulation).

Design principles:
  - Immutable after assembly: EnterpriseContext is frozen (ConfigDict frozen=True).
  - Fully typed: No anonymous dicts. Every section and item carries provenance.
  - Versioned: Schema and instance versions support future migrations.
  - Explainable: Every item carries ContextProvenance — never stripped during compression.
  - Multi-agent safe: Frozen model allows concurrent reads without mutation risk.
  - Provider-agnostic dependency graph: Execution ordering is handled by ContextDependencyGraph.

Lifecycle:
  BUILDING → ASSEMBLED → OPTIMIZED → CONSUMED → EXPIRED → ARCHIVED
  (Enforced by ContextStateMachine in app/services/context/state.py)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import ContextPriority, ContextSource, ContextStatus

# =============================================================================
# Versioning
# =============================================================================


class ContextSchemaVersion(str):
    """Schema version tracking structural evolution of EnterpriseContext.

    Increment when the shape of EnterpriseContext changes in a backward-incompatible way.
    Stored alongside every persisted context record to enable future migration tooling.
    """

    V1 = "1.0"


CURRENT_CONTEXT_SCHEMA_VERSION: str = ContextSchemaVersion.V1


class ContextInstanceVersion(DomainBaseModel):
    """Tracks a single assembled context instance.

    Distinct from schema version: schema version tracks the class definition,
    instance version identifies this specific assembly run.
    """

    context_id: UUID
    schema_version: str = Field(default=CURRENT_CONTEXT_SCHEMA_VERSION)
    assembled_at: datetime
    policy_id: str
    twin_id: UUID


# =============================================================================
# Provenance
# =============================================================================


class ContextProvenance(DomainBaseModel):
    """Explainability metadata attached to every ContextItem.

    Never stripped during compression. Compression updates compression_origin
    and compression_reason to maintain full traceability.
    """

    provider: ContextSource
    service_name: str = Field(..., description="The service class that produced this item.")
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    ranking_score: float = Field(
        default=0.0,
        ge=0.0,
        description="Computed by AbstractContextRanker. Higher = more relevant.",
    )
    compression_origin: list[UUID] = Field(
        default_factory=list,
        description="IDs of original ContextItems this item was compressed from.",
    )
    compression_reason: str | None = Field(
        default=None,
        description="Human-readable reason for compression decision.",
    )
    citations: list[str] = Field(
        default_factory=list,
        description="Source IDs, document refs, or external citations.",
    )
    reasoning_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Opaque engineering metadata. Never exposed to end users.",
    )


# =============================================================================
# Context Items and Sections
# =============================================================================


class ContextItem(DomainBaseModel):
    """A single piece of information within a ContextSection.

    Each item carries full provenance and is independently rankable,
    compressible, and traceable.
    """

    item_id: UUID = Field(default_factory=uuid4)
    source: ContextSource
    priority: ContextPriority = ContextPriority.MEDIUM
    content: str = Field(..., description="Textual representation of this context item.")
    content_type: str = Field(
        default="text",
        description="Format of content: 'text', 'json', 'summary'.",
    )
    domain_object_id: UUID | None = Field(
        default=None,
        description="ID of the underlying domain object (goal ID, memory ID, etc.).",
    )
    token_estimate: int = Field(default=0, ge=0)
    provenance: ContextProvenance
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextSection(DomainBaseModel):
    """A grouped collection of ContextItems from a single provider.

    Sections are the unit of ranking and compression.
    """

    section_id: UUID = Field(default_factory=uuid4)
    source: ContextSource
    priority: ContextPriority = ContextPriority.MEDIUM
    items: list[ContextItem] = Field(default_factory=list)
    token_estimate: int = Field(default=0, ge=0)
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0


# =============================================================================
# Context Window
# =============================================================================


class ContextWindow(DomainBaseModel):
    """The final optimized AI payload produced by AbstractContextWindowBuilder.

    Contains the ranked, compressed, budget-fitted context sections ready for
    injection into PromptContextBuilder → PromptManager → AIKernel.
    """

    window_id: UUID = Field(default_factory=uuid4)
    sections: list[ContextSection] = Field(default_factory=list)
    token_estimate: int = Field(default=0, ge=0)
    budget: int = Field(..., ge=0, description="Configured token budget for this window.")
    items_included: int = Field(default=0, ge=0)
    items_excluded: int = Field(default=0, ge=0)
    overflow: bool = Field(
        default=False,
        description="True if items were excluded due to budget exhaustion.",
    )
    built_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Context Summary
# =============================================================================


class ContextSummary(DomainBaseModel):
    """A compressed narrative summary of an EnterpriseContext.

    Used for UI display and high-level BI reporting.
    Does not replace the full EnterpriseContext — always derived from it.
    """

    summary_id: UUID = Field(default_factory=uuid4)
    context_id: UUID
    twin_id: UUID
    narrative: str = Field(..., description="Human-readable summary of assembled context.")
    source_count: int = Field(default=0)
    token_estimate: int = Field(default=0)
    compression_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Context Metadata (assembly statistics)
# =============================================================================


class ContextMetadata(DomainBaseModel):
    """Assembly statistics and diagnostics for an EnterpriseContext.

    Populated by ContextEngine during assembly. Used by CognitiveTrace and
    operational monitoring.
    """

    schema_version: str = Field(default=CURRENT_CONTEXT_SCHEMA_VERSION)
    policy_id: str
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    total_providers_requested: int = Field(default=0)
    successful_providers: int = Field(default=0)
    failed_providers: int = Field(default=0)
    missing_providers: list[ProviderFailureRecord] = Field(default_factory=list)
    ranking_latency_ms: float | None = None
    compression_latency_ms: float | None = None
    window_latency_ms: float | None = None
    total_assembly_latency_ms: float | None = None
    token_estimate_before_compression: int = Field(default=0)
    token_estimate_after_compression: int = Field(default=0)
    compression_ratio: float | None = None
    items_total: int = Field(default=0)
    items_retained: int = Field(default=0)
    per_provider_latency_ms: dict[str, float] = Field(default_factory=dict)


# =============================================================================
# Provider Failure Record (Extension C)
# =============================================================================


class ProviderFailureRecord(DomainBaseModel):
    """Records a provider failure during EnterpriseContext assembly.

    Stored in EnterpriseContext.metadata.missing_providers.
    Ensures transparency about what information could not be assembled.
    """

    provider: ContextSource
    error_type: str
    error_message: str
    failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    attempts: int = Field(default=1, ge=1)


# =============================================================================
# Provider Metadata (Extension B — Registry)
# =============================================================================


class ProviderMetadata(DomainBaseModel):
    """Metadata about a registered ContextProvider.

    Stored in ContextProviderRegistry alongside the provider instance.
    """

    source: ContextSource
    name: str
    version: str = Field(default="1.0")
    description: str = Field(default="")
    capability_tags: list[str] = Field(default_factory=list)
    is_optional: bool = Field(
        default=True,
        description="If False, failure of this provider aborts assembly.",
    )


# =============================================================================
# Dependency Graph Models (Extension A)
# =============================================================================


class ProviderDependency(DomainBaseModel):
    """Declares a dependency relationship between context providers.

    Used by ContextDependencyGraph to determine execution order.
    """

    provider: ContextSource
    depends_on: list[ContextSource] = Field(
        default_factory=list,
        description="Providers that must complete before this provider executes.",
    )


class ExecutionPlan(DomainBaseModel):
    """Result of topological sorting by ContextDependencyGraph.

    batches: Each inner list contains providers that are safe to run concurrently.
             The outer list is ordered — batch N must complete before batch N+1 starts.
    """

    batches: list[list[ContextSource]]
    total_providers: int


# =============================================================================
# EnterpriseContext — Canonical Cognitive Object
# =============================================================================


class EnterpriseContext(DomainBaseModel):
    """The canonical, immutable, versioned cognitive representation of the business.

    Assembled by ContextEngine from multiple provider sections.
    Consumed by PlanningEngine, RecommendationEngine, and future Agent Framework.

    Design guarantees:
      - Frozen (immutable after assembly): ConfigDict(frozen=True)
      - Fully typed: No anonymous dicts at the section level
      - Versioned: schema_version + instance_version for future migration support
      - Multi-agent safe: Frozen Pydantic model allows concurrent reads without mutation
      - Explainable: All provenance is preserved through compression
    """

    model_config = ConfigDict(frozen=True, from_attributes=True, extra="ignore")

    # --- Identity ---
    context_id: UUID = Field(default_factory=uuid4)
    twin_id: UUID
    schema_version: str = Field(default=CURRENT_CONTEXT_SCHEMA_VERSION)

    # --- Assembly ---
    status: ContextStatus = Field(default=ContextStatus.ASSEMBLED)
    sections: list[ContextSection] = Field(default_factory=list)
    window: ContextWindow | None = Field(
        default=None,
        description="Populated after AbstractContextWindowBuilder runs.",
    )

    # --- Metadata & provenance ---
    metadata: ContextMetadata
    instance_version: ContextInstanceVersion | None = None

    # --- Traceability ---
    intent_id: UUID | None = None
    operation_context_id: str | None = None

    @property
    def source_names(self) -> list[str]:
        """Names of all contributing providers."""
        return [s.source.value for s in self.sections]

    @property
    def total_items(self) -> int:
        return sum(s.item_count for s in self.sections)

    @property
    def token_estimate(self) -> int:
        return sum(s.token_estimate for s in self.sections)

    def get_section(self, source: ContextSource) -> ContextSection | None:
        """Retrieve the section contributed by a specific provider."""
        for section in self.sections:
            if section.source == source:
                return section
        return None


# =============================================================================
# Write Models
# =============================================================================


class EnterpriseContextCreate(DomainBaseModel):
    """Write model for initiating context assembly.

    Passed to ContextEngine.build() to specify what should be assembled.
    """

    twin_id: UUID
    policy_id: str
    intent_id: UUID | None = None
    operation_context_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Lifecycle Metadata (Phase 1.5)
# =============================================================================


class ContextLifecycleMetadata(DomainBaseModel):
    """Mutable sidecar tracking lifecycle transitions for an EnterpriseContext.

    Kept separate from EnterpriseContext to preserve its frozen contract.
    Persisted in enterprise_contexts table.
    """

    context_id: UUID
    twin_id: UUID
    status: ContextStatus = ContextStatus.BUILDING
    policy_id: str
    schema_version: str = Field(default=CURRENT_CONTEXT_SCHEMA_VERSION)
    assembled_at: datetime | None = None
    expires_at: datetime | None = None
    consumed_at: datetime | None = None
    archived_at: datetime | None = None
    is_partial: bool = Field(
        default=False,
        description="True if one or more optional providers failed during assembly.",
    )
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ContextLifecycleCreate(DomainBaseModel):
    """Write model for creating a context lifecycle record."""

    context_id: UUID
    twin_id: UUID
    policy_id: str
    schema_version: str = Field(default=CURRENT_CONTEXT_SCHEMA_VERSION)


class ContextLifecycleUpdate(DomainBaseModel):
    """Write model for transitioning context lifecycle status."""

    status: ContextStatus
    assembled_at: datetime | None = None
    expires_at: datetime | None = None
    consumed_at: datetime | None = None
    archived_at: datetime | None = None
    is_partial: bool | None = None


# =============================================================================
# Pagination
# =============================================================================


class PaginatedContextLifecycles(DomainBaseModel):
    """Pagination wrapper for context lifecycle listings."""

    items: list[ContextLifecycleMetadata]
    total_count: int
    limit: int
    offset: int
