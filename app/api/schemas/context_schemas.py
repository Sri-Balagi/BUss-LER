"""Public API schemas for Context Engine and Conversations."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ContextStatus, ConversationStatus, ConversationRole
from app.models.enterprise_context import (
    ContextMetadata,
    ContextLifecycleMetadata,
    ContextWindow,
    ContextSection,
)
from app.models.conversation import ConversationThread, ConversationTurn


# =============================================================================
# Context Engine API Schemas
# =============================================================================

class BuildContextRequest(BaseModel):
    """Request to force-build an EnterpriseContext."""
    policy_id: str = Field(default="full", description="ID of the ContextPolicy to apply.")
    intent_id: Optional[UUID] = Field(default=None, description="Optional Intent ID that triggered this build.")


class ContextLifecycleResponse(BaseModel):
    """Response representing a Context Lifecycle record (metadata only)."""
    id: UUID
    twin_id: UUID
    policy_id: str
    schema_version: str
    status: ContextStatus
    is_partial: bool
    assembled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    consumed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PaginatedContextLifecyclesResponse(BaseModel):
    """Paginated list of context lifecycles."""
    items: List[ContextLifecycleResponse]
    total_count: int
    limit: int
    offset: int


class EnterpriseContextResponse(BaseModel):
    """Full EnterpriseContext response (only returned during live builds or from cache)."""
    context_id: UUID
    twin_id: UUID
    intent_id: Optional[UUID] = None
    operation_context_id: Optional[str] = None
    status: ContextStatus
    metadata: ContextMetadata
    window: ContextWindow
    sections: List[ContextSection]


# =============================================================================
# Conversation API Schemas
# =============================================================================

class ConversationThreadCreateRequest(BaseModel):
    """Request to create a new conversation thread."""
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationThreadResponse(BaseModel):
    """Response for a conversation thread."""
    id: UUID
    twin_id: UUID
    title: Optional[str]
    status: ConversationStatus
    summary: Optional[str]
    turn_count: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PaginatedConversationThreadsResponse(BaseModel):
    """Paginated list of conversation threads."""
    items: List[ConversationThreadResponse]
    total_count: int
    limit: int
    offset: int


class ConversationTurnCreateRequest(BaseModel):
    """Request to append a turn to a conversation."""
    role: ConversationRole
    content: str
    agent_id: Optional[UUID] = None
    tokens_used: int = 0
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationTurnResponse(BaseModel):
    """Response for a conversation turn."""
    id: UUID
    thread_id: UUID
    role: ConversationRole
    content: str
    agent_id: Optional[UUID]
    tokens_used: int
    tool_calls: List[Dict[str, Any]]
    turn_index: int
    metadata: Dict[str, Any]
    created_at: datetime
