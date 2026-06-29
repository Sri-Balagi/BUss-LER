"""Conversation domain models — Milestone 4.

Conversation provides short-term working memory for the Context Engine.
It is distinct from the Memory Engine (which provides long-term semantic memory).

Conversation threads are twin-scoped and persisted in Supabase.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.shared.enums import ConversationRole, ConversationStatus
from app.interfaces.http.schemas.base import DomainBaseModel


# =============================================================================
# Conversation Thread
# =============================================================================


class ConversationThread(DomainBaseModel):
    """A named conversation session between a user and the AI.

    Provides short-term working memory.  Each thread belongs to a Digital Twin.
    """

    id: UUID
    twin_id: UUID
    title: Optional[str] = Field(default=None, max_length=500)
    status: ConversationStatus = ConversationStatus.ACTIVE
    summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the conversation so far.",
    )
    turn_count: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None


class ConversationThreadCreate(DomainBaseModel):
    """Write model for starting a new conversation thread."""

    twin_id: UUID
    title: Optional[str] = Field(default=None, max_length=500)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Conversation Turn
# =============================================================================


class ConversationTurn(DomainBaseModel):
    """A single exchange within a ConversationThread.

    Ordered by turn_index. Role follows ConversationRole: user, assistant, system, tool.
    """

    id: UUID
    thread_id: UUID
    role: ConversationRole
    content: str = Field(..., min_length=1, max_length=50000)
    agent_id: Optional[UUID] = Field(
        default=None,
        description="Agent that produced this turn (for assistant/tool roles).",
    )
    tokens_used: int = Field(default=0, ge=0)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    turn_index: int = Field(..., ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ConversationTurnCreate(DomainBaseModel):
    """Write model for appending a turn to a thread."""

    thread_id: UUID
    role: ConversationRole
    content: str = Field(..., min_length=1, max_length=50000)
    agent_id: Optional[UUID] = None
    tokens_used: int = Field(default=0, ge=0)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Conversation with Turns (read model)
# =============================================================================


class ConversationWithTurns(DomainBaseModel):
    """Conversation thread with all of its turns included."""

    thread: ConversationThread
    turns: List[ConversationTurn] = Field(default_factory=list)


# =============================================================================
# Pagination
# =============================================================================


class PaginatedConversationThreads(DomainBaseModel):
    """Pagination wrapper for conversation thread listings."""

    items: List[ConversationThread]
    total_count: int
    limit: int
    offset: int


class PaginatedConversationTurns(DomainBaseModel):
    """Pagination wrapper for conversation turn listings."""

    items: List[ConversationTurn]
    total_count: int
    limit: int
    offset: int
