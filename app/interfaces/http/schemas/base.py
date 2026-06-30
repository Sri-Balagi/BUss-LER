"""BizOS domain schemas.

Pydantic v2 models representing the Business Foundation Model (BFM).
These models enforce validation rules and act as data transfer objects.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import (
    ActionStatus,
    ActionType,
    ConstraintSeverity,
    ConstraintType,
    ConversationRole,
    ConversationStatus,
    EntityType,
    GoalStatus,
    GoalType,
    OutcomeVerdict,
    ResourceType,
)

# =============================================================================
# Base Models
# =============================================================================


class DomainBaseModel(BaseModel):
    """Base class for all domain models with common configuration."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")


# =============================================================================
# Entity Models
# =============================================================================


class EntityCreate(DomainBaseModel):
    """Request schema for creating an entity."""

    name: str = Field(..., min_length=1, max_length=200)
    entity_type: EntityType
    description: str | None = Field(None, max_length=2000)
    metadata: dict = Field(default_factory=dict)


class Entity(DomainBaseModel):
    """Full entity object from database."""

    id: UUID
    user_id: UUID
    name: str
    entity_type: EntityType
    description: str | None
    metadata: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Goal Models
# =============================================================================


class GoalCreate(DomainBaseModel):
    """Request schema for creating a goal."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    goal_type: GoalType = GoalType.STRATEGIC
    parent_goal_id: UUID | None = None
    priority: int = Field(default=5, ge=1, le=10)
    target_date: datetime | None = None
    success_criteria: list[str] = Field(default_factory=list)


class Goal(DomainBaseModel):
    """Full goal object."""

    id: UUID
    entity_id: UUID
    parent_goal_id: UUID | None
    title: str
    description: str | None
    goal_type: GoalType
    status: GoalStatus
    priority: int
    progress: float
    success_criteria: list[str]
    target_date: datetime | None
    completed_at: datetime | None
    ai_plan: dict
    blockers: list[dict]
    adaptations: list[dict]
    depth: int
    path: list[str]
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Resource Models (Stored in JSONB inside Digital Twin in MVP)
# =============================================================================


class Resource(DomainBaseModel):
    """A resource available to the entity."""

    id: UUID
    entity_id: UUID
    resource_type: ResourceType
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None
    quantity: float | None = Field(None, ge=0.0)
    unit: str | None
    metadata: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Constraint Models (Stored in JSONB inside Digital Twin in MVP)
# =============================================================================


class Constraint(DomainBaseModel):
    """A constraint limiting the entity."""

    id: UUID
    entity_id: UUID
    constraint_type: ConstraintType
    description: str = Field(..., min_length=1, max_length=1000)
    severity: ConstraintSeverity
    is_active: bool
    metadata: dict
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Action Models
# =============================================================================


class Action(DomainBaseModel):
    """An action taken by an agent or the system."""

    id: UUID
    entity_id: UUID
    agent_id: UUID | None
    goal_id: UUID | None
    action_type: ActionType
    action_detail: dict
    status: ActionStatus
    expected_outcome: str | None
    actual_outcome: str | None
    tokens_input: int = Field(default=0, ge=0)
    tokens_output: int = Field(default=0, ge=0)
    duration_ms: int = Field(default=0, ge=0)
    requires_approval: bool
    error_message: str | None
    created_at: datetime


# =============================================================================
# Outcome Models
# =============================================================================


class Outcome(DomainBaseModel):
    """Evaluation of an action's result."""

    id: UUID
    entity_id: UUID
    action_id: UUID
    goal_id: UUID | None
    expected: str = Field(..., min_length=1, max_length=5000)
    actual: str = Field(..., min_length=1, max_length=5000)
    verdict: OutcomeVerdict
    lessons: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    should_update_twin: bool
    twin_updates: dict
    created_at: datetime


# =============================================================================
# Conversation Models
# =============================================================================


class ConversationCreate(DomainBaseModel):
    """Request schema for starting a conversation."""

    title: str | None = Field(None, max_length=500)
    metadata: dict = Field(default_factory=dict)


class Conversation(DomainBaseModel):
    """Conversation read model."""

    id: UUID
    entity_id: UUID
    title: str | None
    status: ConversationStatus
    summary: str | None
    turn_count: int
    metadata: dict
    created_at: datetime
    updated_at: datetime


class TurnCreate(DomainBaseModel):
    """Request schema for adding a conversation turn."""

    role: ConversationRole
    content: str = Field(..., min_length=1, max_length=50000)


class ConversationTurn(DomainBaseModel):
    """A single turn in a conversation."""

    id: UUID
    conversation_id: UUID
    role: ConversationRole
    content: str
    agent_id: UUID | None
    tokens_used: int
    tool_calls: list[dict]
    turn_index: int
    created_at: datetime


class ConversationWithTurns(DomainBaseModel):
    """Conversation with all its turns."""

    conversation: Conversation
    turns: list[ConversationTurn]
