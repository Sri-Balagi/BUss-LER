"""BizOS domain enumerations.

All enum types used across the Business Foundation Model.
These are the categorical values that constrain the domain objects.
"""

from enum import StrEnum

# =============================================================================
# Entity Enums
# =============================================================================


class EntityType(StrEnum):
    """Type of entity that BizOS manages."""

    INDIVIDUAL = "individual"
    STARTUP = "startup"
    SMALL_BUSINESS = "small_business"
    STUDENT = "student"
    ORGANIZATION = "organization"


# =============================================================================
# Goal Enums
# =============================================================================


class GoalType(StrEnum):
    """Hierarchical level of a goal."""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    HABIT = "habit"


class GoalPriority(StrEnum):
    """Priority level of a goal."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(StrEnum):
    """Lifecycle status of a goal."""

    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"


# =============================================================================
# Resource Enums
# =============================================================================


class ResourceType(StrEnum):
    """Category of resource available to an entity."""

    FINANCIAL = "financial"
    HUMAN = "human"
    TOOL = "tool"
    TIME = "time"
    KNOWLEDGE = "knowledge"
    NETWORK = "network"


# =============================================================================
# Constraint Enums
# =============================================================================


class ConstraintType(StrEnum):
    """Category of constraint limiting an entity."""

    FINANCIAL = "financial"
    TEMPORAL = "temporal"
    REGULATORY = "regulatory"
    PERSONAL = "personal"
    TECHNICAL = "technical"


class ConstraintSeverity(StrEnum):
    """How strict a constraint is."""

    HARD = "hard"
    SOFT = "soft"


# =============================================================================
# Memory Enums
# =============================================================================


class MemoryCategory(StrEnum):
    """Business-oriented classification of a memory."""

    OBSERVATION = "observation"
    EVENT = "event"
    INTERACTION = "interaction"
    DECISION = "decision"
    TASK = "task"
    REFLECTION = "reflection"
    GOAL_PROGRESS = "goal_progress"
    ALERT = "alert"
    SYSTEM = "system"


class EmbeddingStatus(StrEnum):
    """Lifecycle status of a memory embedding process."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MemorySource(StrEnum):
    """Origin of a memory."""

    CONVERSATION = "conversation"
    DOCUMENT = "document"
    EXECUTION = "execution"
    OBSERVATION = "observation"
    USER_INPUT = "user_input"


# =============================================================================
# Action Enums
# =============================================================================


class ActionType(StrEnum):
    """Type of action performed by an agent or the system."""

    LLM_INFERENCE = "llm_inference"
    TOOL_CALL = "tool_call"
    NOTIFICATION = "notification"
    STATE_UPDATE = "state_update"
    MEMORY_WRITE = "memory_write"


class ActionStatus(StrEnum):
    """Lifecycle status of an action."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    NEEDS_APPROVAL = "needs_approval"
    CANCELLED = "cancelled"


# =============================================================================
# Outcome Enums
# =============================================================================


class OutcomeVerdict(StrEnum):
    """Evaluation verdict for an action's result."""

    AS_EXPECTED = "as_expected"
    BETTER = "better_than_expected"
    WORSE = "worse_than_expected"
    UNEXPECTED = "unexpected"
    FAILED = "failed"


# =============================================================================
# Conversation Enums
# =============================================================================


class ConversationStatus(StrEnum):
    """Status of a conversation."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class ConversationRole(StrEnum):
    """Role of a conversation turn participant."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


# =============================================================================
# Intent Enums
# =============================================================================


class IntentType(StrEnum):
    """Business-domain classification of a user intent."""

    INVENTORY = "inventory"
    CALENDAR = "calendar"
    ANALYTICS = "analytics"
    FINANCE = "finance"
    COMMUNICATION = "communication"
    TASK_MANAGEMENT = "task_management"
    REPORTING = "reporting"
    RESEARCH = "research"
    GENERAL = "general"


class IntentStatus(StrEnum):
    """Lifecycle status of an intent."""

    PENDING = "pending"
    CLASSIFIED = "classified"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class IntentConfidence(StrEnum):
    """AI classification confidence band for an intent."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# Plan Enums
# =============================================================================


class PlanStatus(StrEnum):
    """Lifecycle status of a generated plan."""

    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# =============================================================================
# Recommendation Enums
# =============================================================================


class RecommendationStatus(StrEnum):
    """Lifecycle status of a proactive recommendation."""

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RecommendationConfidence(StrEnum):
    """AI confidence band for a generated recommendation."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# Context Engine Enums (Milestone 4)
# =============================================================================


class ContextSource(StrEnum):
    """Identifies which cognitive subsystem contributed a context section."""

    MEMORY = "memory"
    INTENT = "intent"
    GOAL = "goal"
    PLAN = "plan"
    RECOMMENDATION = "recommendation"
    TWIN = "twin"
    CONVERSATION = "conversation"
    TRACE = "trace"
    BUSINESS_STATE = "business_state"
    EXTERNAL = "external"


class ContextStatus(StrEnum):
    """Lifecycle status of an EnterpriseContext assembly."""

    BUILDING = "building"
    ASSEMBLED = "assembled"
    OPTIMIZED = "optimized"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class ContextPriority(StrEnum):
    """Priority tier for a context section or item."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class RefreshStrategy(StrEnum):
    """Cache refresh strategy for a context provider."""

    LAZY = "lazy"  # Refresh only on cache miss
    EAGER = "eager"  # Refresh in background before expiry
    FORCED = "forced"  # Always re-fetch, bypass cache


# =============================================================================
