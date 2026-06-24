"""BizOS domain enumerations.

All enum types used across the Business Foundation Model.
These are the categorical values that constrain the domain objects.
"""

from enum import Enum


# =============================================================================
# Entity Enums
# =============================================================================


class EntityType(str, Enum):
    """Type of entity that BizOS manages."""

    INDIVIDUAL = "individual"
    STARTUP = "startup"
    SMALL_BUSINESS = "small_business"
    STUDENT = "student"
    ORGANIZATION = "organization"


# =============================================================================
# Goal Enums
# =============================================================================


class GoalType(str, Enum):
    """Hierarchical level of a goal."""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    HABIT = "habit"


class GoalStatus(str, Enum):
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


class ResourceType(str, Enum):
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


class ConstraintType(str, Enum):
    """Category of constraint limiting an entity."""

    FINANCIAL = "financial"
    TEMPORAL = "temporal"
    REGULATORY = "regulatory"
    PERSONAL = "personal"
    TECHNICAL = "technical"


class ConstraintSeverity(str, Enum):
    """How strict a constraint is."""

    HARD = "hard"
    SOFT = "soft"


# =============================================================================
# Memory Enums
# =============================================================================


class MemoryType(str, Enum):
    """Type of long-term memory."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemorySource(str, Enum):
    """Origin of a memory."""

    CONVERSATION = "conversation"
    DOCUMENT = "document"
    EXECUTION = "execution"
    OBSERVATION = "observation"
    USER_INPUT = "user_input"


# =============================================================================
# Action Enums
# =============================================================================


class ActionType(str, Enum):
    """Type of action performed by an agent or the system."""

    LLM_INFERENCE = "llm_inference"
    TOOL_CALL = "tool_call"
    NOTIFICATION = "notification"
    STATE_UPDATE = "state_update"
    MEMORY_WRITE = "memory_write"


class ActionStatus(str, Enum):
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


class OutcomeVerdict(str, Enum):
    """Evaluation verdict for an action's result."""

    AS_EXPECTED = "as_expected"
    BETTER = "better_than_expected"
    WORSE = "worse_than_expected"
    UNEXPECTED = "unexpected"
    FAILED = "failed"


# =============================================================================
# Conversation Enums
# =============================================================================


class ConversationStatus(str, Enum):
    """Status of a conversation."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class ConversationRole(str, Enum):
    """Role of a conversation turn participant."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
