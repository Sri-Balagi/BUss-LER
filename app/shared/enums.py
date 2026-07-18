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

class PrincipalType(str, Enum):
    """Type of execution principal."""
    
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"

class ParticipantRole(str, Enum):
    """Role of a session participant."""
    
    OWNER = "OWNER"
    OBSERVER = "OBSERVER"
    CONTRIBUTOR = "CONTRIBUTOR"
    COORDINATOR = "COORDINATOR"

class AgentType(str, Enum):
    """Type of autonomous agent."""
    
    PLANNER = "PLANNER"
    RESEARCH = "RESEARCH"
    REASONING = "REASONING"
    EXECUTOR = "EXECUTOR"
    MEMORY = "MEMORY"
    CUSTOM = "CUSTOM"

class AgentStatus(str, Enum):
    """Lifecycle status of an agent."""
    
    REGISTERED = "REGISTERED"
    READY = "READY"
    BUSY = "BUSY"
    BLOCKED = "BLOCKED"
    OFFLINE = "OFFLINE"
    FAILED = "FAILED"


# =============================================================================
# Goal Enums
# =============================================================================


class GoalType(str, Enum):
    """Hierarchical level of a goal."""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    HABIT = "habit"


class GoalPriority(str, Enum):
    """Priority level of a goal."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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


class MemoryCategory(str, Enum):
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


class EmbeddingStatus(str, Enum):
    """Lifecycle status of a memory embedding process."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


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


# =============================================================================
# Intent Enums
# =============================================================================


class IntentType(str, Enum):
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


class IntentStatus(str, Enum):
    """Lifecycle status of an intent."""

    PENDING = "pending"
    CLASSIFIED = "classified"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class IntentConfidence(str, Enum):
    """AI classification confidence band for an intent."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# Plan Enums
# =============================================================================


class PlanStatus(str, Enum):
    """Lifecycle status of a generated plan."""

    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# =============================================================================
# Recommendation Enums
# =============================================================================


class RecommendationStatus(str, Enum):
    """Lifecycle status of a proactive recommendation."""

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RecommendationConfidence(str, Enum):
    """AI confidence band for a generated recommendation."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# Context Engine Enums (Milestone 4)
# =============================================================================


class ContextSource(str, Enum):
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


class ContextStatus(str, Enum):
    """Lifecycle status of an EnterpriseContext assembly."""

    BUILDING = "building"
    ASSEMBLED = "assembled"
    OPTIMIZED = "optimized"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class ContextPriority(str, Enum):
    """Priority tier for a context section or item."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class RefreshStrategy(str, Enum):
    """Cache refresh strategy for a context provider."""

    LAZY = "lazy"  # Refresh only on cache miss
    EAGER = "eager"  # Refresh in background before expiry
    FORCED = "forced"  # Always re-fetch, bypass cache


# =============================================================================
