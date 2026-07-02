"""Public API schemas for Context Engine and Conversations."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.intelligence.intake.situation.enterprise_context import (
    ContextMetadata,
    ContextSection,
    ContextWindow,
)
from app.shared.enums import ContextStatus, ConversationRole, ConversationStatus

# =============================================================================
# Context Engine API Schemas
# =============================================================================


class BuildContextRequest(BaseModel):
    """Request to force-build an EnterpriseContext."""

    policy_id: str = Field(default="full", description="ID of the ContextPolicy to apply.")
    intent_id: UUID | None = Field(
        default=None, description="Optional Intent ID that triggered this build."
    )


class ContextLifecycleResponse(BaseModel):
    """Response representing a Context Lifecycle record (metadata only)."""

    id: UUID
    twin_id: UUID
    policy_id: str
    schema_version: str
    status: ContextStatus
    is_partial: bool
    assembled_at: datetime | None = None
    expires_at: datetime | None = None
    consumed_at: datetime | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PaginatedContextLifecyclesResponse(BaseModel):
    """Paginated list of context lifecycles."""

    items: list[ContextLifecycleResponse]
    total_count: int
    limit: int
    offset: int


class EnterpriseContextResponse(BaseModel):
    """Full EnterpriseContext response (only returned during live builds or from cache)."""

    context_id: UUID
    twin_id: UUID
    intent_id: UUID | None = None
    operation_context_id: str | None = None
    status: ContextStatus
    metadata: ContextMetadata
    window: ContextWindow
    sections: list[ContextSection]


# =============================================================================
# Conversation API Schemas
# =============================================================================


class ConversationThreadCreateRequest(BaseModel):
    """Request to create a new conversation thread."""

    title: str | None = None
    metadata: dict[str, Any] | None = None


class ConversationThreadResponse(BaseModel):
    """Response for a conversation thread."""

    id: UUID
    twin_id: UUID
    title: str | None
    status: ConversationStatus
    summary: str | None
    turn_count: int
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PaginatedConversationThreadsResponse(BaseModel):
    """Paginated list of conversation threads."""

    items: list[ConversationThreadResponse]
    total_count: int
    limit: int
    offset: int


class ConversationTurnCreateRequest(BaseModel):
    """Request to append a turn to a conversation."""

    role: ConversationRole
    content: str
    agent_id: UUID | None = None
    tokens_used: int = 0
    tool_calls: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class ConversationTurnResponse(BaseModel):
    """Response for a conversation turn."""

    id: UUID
    thread_id: UUID
    role: ConversationRole
    content: str
    agent_id: UUID | None
    tokens_used: int
    tool_calls: list[dict[str, Any]]
    turn_index: int
    metadata: dict[str, Any]
    created_at: datetime
