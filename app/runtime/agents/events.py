from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _now() -> datetime:
    return datetime.now(UTC)

@dataclass
class AgentLifecycleEvent:
    """Base class for all internal runtime agent events."""
    agent_id: str
    task_id: str
    timestamp: datetime = field(default_factory=_now)

@dataclass
class AgentInitialized(AgentLifecycleEvent):
    pass

@dataclass
class AgentReady(AgentLifecycleEvent):
    pass

@dataclass
class AgentExecuting(AgentLifecycleEvent):
    pass

@dataclass
class AgentWaiting(AgentLifecycleEvent):
    reason: str = ""

@dataclass
class AgentSuspended(AgentLifecycleEvent):
    reason: str = ""

@dataclass
class AgentCompleted(AgentLifecycleEvent):
    metrics: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentFailed(AgentLifecycleEvent):
    error: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentShutdown(AgentLifecycleEvent):
    pass
