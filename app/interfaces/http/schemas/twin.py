"""Digital Twin domain models.

Pydantic v2 models for the Digital Twin System including:
- Digital Twin (the living, versioned state object)
- Twin Snapshot (immutable point-in-time state captures)
- Twin History (audit log of all changes)

Architecture:
    The Digital Twin uses a domain-agnostic design with two JSONB fields:

    - ``state``: The primary representation of the entity's current state.
      Keys are free-form and determined by the consuming engine or user.
      Examples: {"demographics": {...}, "finances": {...}} for an entrepreneur,
      or {"rooms": {...}, "staff": {...}} for a hotel.

    - ``metadata``: System-level information structured via ``TwinMetadata``.
      Contains schema_version, labels, external_ids, source tracking.
      Separate from state to keep domain data clean.

    This design ensures the schema never needs to change as BizOS
    expands to new entity types (students, restaurants, hotels, etc.).
    Future engines (Memory, Goals, Context, Agents, Simulation) define
    their own key conventions within ``state``.

Schema Versioning:
    Every twin carries a ``schema_version`` inside its metadata.
    This enables forward-compatible migrations, backward compatibility,
    and data transformation pipelines as BizOS evolves.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.interfaces.http.schemas.base import DomainBaseModel

# =============================================================================
# Constants
# =============================================================================

CURRENT_SCHEMA_VERSION: int = 1
"""The current schema version for newly created Digital Twins.

Increment this when the internal structure of ``state`` or ``metadata``
changes in a way that requires migration of existing twin data.
"""


# =============================================================================
# Enums
# =============================================================================


class ChangeType(str, Enum):
    """Type of change recorded in twin history.

    Used by TwinHistory to categorize each audit entry.
    Stored as lowercase string in the database with CHECK constraint.
    """

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# =============================================================================
# Structured Metadata
# =============================================================================


class TwinMetadata(BaseModel):
    """System-level metadata for a Digital Twin.

    This model defines the known metadata fields while allowing
    arbitrary extension via ``extra="allow"``. It is stored as
    JSONB in the database and serialized/deserialized automatically.

    The ``schema_version`` field is critical for forward compatibility:
    it allows future data migration pipelines to detect and transform
    older twin data formats.
    """

    model_config = ConfigDict(extra="allow")

    schema_version: int = Field(
        default=CURRENT_SCHEMA_VERSION,
        ge=1,
        description=(
            "Schema version for this twin's data format. "
            "Used for forward-compatible migrations."
        ),
    )
    created_by: str | None = Field(
        None,
        max_length=200,
        description="Identifier of who/what created this twin (user, system, agent).",
    )
    updated_by: str | None = Field(
        None,
        max_length=200,
        description="Identifier of who/what last updated this twin.",
    )
    source: str | None = Field(
        None,
        max_length=200,
        description="Origin of the twin data (api, import, migration, etc.).",
    )
    labels: list[str] = Field(
        default_factory=list,
        description="Free-form labels for categorization and filtering.",
    )
    external_ids: dict = Field(
        default_factory=dict,
        description=(
            "External system identifiers. "
            "Example: {'crm_id': '...', 'stripe_id': '...'}"
        ),
    )


# =============================================================================
# Request / Input Models
# =============================================================================


class DigitalTwinCreate(DomainBaseModel):
    """Request schema for creating a Digital Twin.

    A Digital Twin is created independently of its Entity (they have
    separate lifecycles). The ``entity_id`` must reference an existing
    entity. Each entity can have at most one twin (UNIQUE constraint).

    The ``state`` field is intentionally unstructured — its internal
    organization is determined by the consuming engine or user.

    The ``metadata`` field defaults to a ``TwinMetadata`` instance
    with ``schema_version`` set to ``CURRENT_SCHEMA_VERSION``.
    """

    entity_id: UUID = Field(
        ...,
        description="The entity this twin represents. Must be unique per entity.",
    )
    state: dict = Field(
        default_factory=dict,
        description=(
            "Initial state of the twin. Free-form JSONB — keys are "
            "determined by the consuming engine or user. "
            "Example: {'demographics': {...}, 'finances': {...}}"
        ),
    )
    metadata: TwinMetadata = Field(
        default_factory=TwinMetadata,
        description=(
            "System-level metadata including schema_version, labels, "
            "external_ids, and source tracking."
        ),
    )


class DigitalTwinUpdate(DomainBaseModel):
    """Request schema for updating a Digital Twin.

    **State merging**: If ``state`` is provided, its top-level keys are
    merged into the existing state. Keys present in the update replace
    the corresponding keys in the current state. Keys not included in
    the update are preserved. This enables partial updates at the
    dimension level without requiring the full state.

    **Metadata replacement**: If ``metadata`` is provided, it replaces
    the entire metadata object. The service layer is responsible for
    preserving ``schema_version`` if the caller omits it.

    **Optimistic concurrency**: The ``expected_version`` field is
    **required**. If the current twin version does not match, the
    update is rejected with HTTP 409 Conflict.
    """

    expected_version: int = Field(
        ...,
        ge=1,
        description=(
            "Expected current version of the twin. "
            "Used for optimistic concurrency — if the actual version "
            "differs, the update is rejected (HTTP 409)."
        ),
    )
    state: dict | None = Field(
        None,
        description=(
            "Partial state update. Top-level keys are merged into the "
            "existing state. Omitted keys are preserved."
        ),
    )
    metadata: dict | None = Field(
        None,
        description=(
            "Updated metadata. Replaces the entire metadata object. "
            "Caller should include schema_version; the service layer "
            "preserves it if omitted."
        ),
    )
    change_reason: str | None = Field(
        None,
        max_length=500,
        description="Human-readable reason for the update (stored in snapshot and history).",
    )
    changed_by: str | None = Field(
        None,
        max_length=200,
        description="Identifier of who/what initiated the change (user, agent, system).",
    )


# =============================================================================
# Read / Response Models
# =============================================================================


class DigitalTwin(DomainBaseModel):
    """Full Digital Twin read model from database.

    Represents the complete current state of a Digital Twin.
    The ``state`` field is domain-agnostic — its structure is
    determined by the consuming engine or user, not by the schema.
    """

    id: UUID
    entity_id: UUID
    state: dict = Field(
        description="The entity's current state. Free-form JSONB.",
    )
    metadata: TwinMetadata = Field(
        description="System-level metadata including schema_version.",
    )
    twin_version: int = Field(
        description="Monotonically increasing version number. Starts at 1.",
    )
    last_snapshot_at: datetime | None = Field(
        description="Timestamp of the most recent snapshot. None if never updated.",
    )
    created_at: datetime
    updated_at: datetime


class TwinSnapshot(DomainBaseModel):
    """Immutable point-in-time copy of a Digital Twin's state.

    Snapshots are created automatically on every twin update inside
    the same database transaction. They are **immutable** — no
    update or delete operations are supported.

    The ``snapshot_data`` field contains the full twin state,
    metadata (including schema_version), and version number
    at the moment the snapshot was taken.
    """

    id: UUID
    twin_id: UUID = Field(
        description="The Digital Twin this snapshot belongs to.",
    )
    twin_version: int = Field(
        description="The twin version at the time this snapshot was taken.",
    )
    snapshot_data: dict = Field(
        description=(
            "Complete twin state + metadata at snapshot time. "
            "Contains 'state', 'metadata', and 'twin_version' keys."
        ),
    )
    change_reason: str | None = Field(
        description="Human-readable reason for the change that triggered this snapshot.",
    )
    created_at: datetime


class TwinHistory(DomainBaseModel):
    """Audit log entry for a Digital Twin change.

    Every create, update, and delete operation on a twin is
    recorded as a history entry with full change tracking including:

    - Which state keys changed
    - Old values (before the change)
    - New values (after the change)
    - Who/what initiated the change
    - Why the change was made
    """

    id: UUID
    twin_id: UUID = Field(
        description="The Digital Twin this history entry belongs to.",
    )
    twin_version: int = Field(
        description="The twin version after this change was applied.",
    )
    change_type: ChangeType = Field(
        description="Type of change: CREATE, UPDATE, or DELETE.",
    )
    change_summary: str | None = Field(
        description="Human-readable summary of what changed.",
    )
    changed_fields: list[str] = Field(
        default_factory=list,
        description=(
            "List of top-level state keys that were modified. "
            "Includes 'metadata' if metadata was changed."
        ),
    )
    changed_by: str | None = Field(
        description="Identifier of who/what initiated the change.",
    )
    old_values: dict | None = Field(
        description="Previous values of the changed fields (None for 'create').",
    )
    new_values: dict | None = Field(
        description="New values of the changed fields (None for 'delete').",
    )
    created_at: datetime
