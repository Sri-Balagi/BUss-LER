"""BizOS command models — inputs to service write operations.

Commands follow the CQRS pattern: one command = one intent to mutate state.
No business logic lives here; commands are pure data containers.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import Field

from app.models.schemas import DomainBaseModel
from app.models.enums import (
    GoalStatus,
    GoalType,
    IntentStatus,
    MemoryCategory,
    MemorySource,
    PlanStatus,
    RecommendationStatus,
)


# =============================================================================
# Memory Commands (Milestone 2)
# =============================================================================


class CreateMemoryCommand(DomainBaseModel):
    """Command to create a new memory."""

    twin_id: uuid.UUID
    content: str
    title: str = "Untitled"
    source: MemorySource = MemorySource.USER_INPUT
    memory_category: MemoryCategory = MemoryCategory.OBSERVATION
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class DeleteMemoryCommand(DomainBaseModel):
    """Command to soft-delete a memory."""

    memory_id: uuid.UUID


class RestoreMemoryCommand(DomainBaseModel):
    """Command to restore a soft-deleted memory."""

    memory_id: uuid.UUID


# =============================================================================
# Intent Commands (Milestone 3)
# =============================================================================


class CreateIntentCommand(DomainBaseModel):
    """Command to create a new raw intent (before classification)."""

    twin_id: uuid.UUID
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClassifyIntentCommand(DomainBaseModel):
    """Command to classify an existing intent using AIKernel.classify()."""

    intent_id: uuid.UUID
    twin_id: uuid.UUID


class UpdateIntentStatusCommand(DomainBaseModel):
    """Command to transition an intent's lifecycle status via IntentStateMachine."""

    intent_id: uuid.UUID
    target_status: IntentStatus


class DeleteIntentCommand(DomainBaseModel):
    """Command to soft-delete an intent."""

    intent_id: uuid.UUID


# =============================================================================
# Goal Commands (Milestone 3)
# =============================================================================


class CreateGoalCommand(DomainBaseModel):
    """Command to create a new goal."""

    twin_id: uuid.UUID
    title: str
    description: Optional[str] = None
    goal_type: GoalType = GoalType.STRATEGIC
    priority: int = Field(default=5, ge=1, le=10)
    target_date: Optional[datetime] = None
    success_criteria: List[str] = Field(default_factory=list)
    parent_goal_id: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateGoalCommand(DomainBaseModel):
    """Command to update a goal's attributes."""

    goal_id: uuid.UUID
    title: Optional[str] = None
    description: Optional[str] = None
    goal_type: Optional[GoalType] = None
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    target_date: Optional[datetime] = None
    success_criteria: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class UpdateGoalProgressCommand(DomainBaseModel):
    """Command to update a goal's completion progress."""

    goal_id: uuid.UUID
    progress: float = Field(..., ge=0.0, le=100.0)


class UpdateGoalStatusCommand(DomainBaseModel):
    """Command to transition a goal's lifecycle status via GoalStateMachine."""

    goal_id: uuid.UUID
    target_status: GoalStatus


class LinkIntentToGoalCommand(DomainBaseModel):
    """Command to create an association between an Intent and a Goal."""

    intent_id: uuid.UUID
    goal_id: uuid.UUID


class DeleteGoalCommand(DomainBaseModel):
    """Command to soft-delete a goal."""

    goal_id: uuid.UUID


# =============================================================================
# Plan Commands (Milestone 3)
# =============================================================================


class GeneratePlanCommand(DomainBaseModel):
    """Command to generate a plan for a goal using the PlanningEngine."""

    twin_id: uuid.UUID
    goal_id: Optional[uuid.UUID] = None
    intent_id: Optional[uuid.UUID] = None


class UpdatePlanStatusCommand(DomainBaseModel):
    """Command to transition a plan's lifecycle status via PlanStateMachine."""

    plan_id: uuid.UUID
    target_status: PlanStatus


# =============================================================================
# Recommendation Commands (Milestone 3)
# =============================================================================


class GenerateRecommendationsCommand(DomainBaseModel):
    """Command to generate proactive recommendations for a twin."""

    twin_id: uuid.UUID
    intent_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional intent to ground the recommendation generation.",
    )


class UpdateRecommendationStatusCommand(DomainBaseModel):
    """Command to update a recommendation's user response status."""

    recommendation_id: uuid.UUID
    target_status: RecommendationStatus
