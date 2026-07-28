"""Decoupled Platform Lifecycle Events for BizOS Wave 0-12 Architecture."""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from app.shared.events.models import DomainEvent


@dataclass
class IntentCreatedEvent(DomainEvent):
    intent_id: str
    tenant_id: str
    intent_type: str
    raw_query: str
    confidence: float = 0.95


@dataclass
class PlanCreatedEvent(DomainEvent):
    plan_id: str
    goal_id: str
    workflow_id: str
    step_count: int
    assigned_agents: list[str] = None


@dataclass
class GoalStartedEvent(DomainEvent):
    goal_id: str
    objective: str
    priority: str


@dataclass
class WorkflowStartedEvent(DomainEvent):
    workflow_id: str
    initial_step: str


@dataclass
class WorkflowCompletedEvent(DomainEvent):
    workflow_id: str
    status: str
    elapsed_ms: float


@dataclass
class MemoryStoredEvent(DomainEvent):
    memory_id: str
    memory_type: str
    title: str


@dataclass
class GoalCompletedEvent(DomainEvent):
    goal_id: str
    status: str
    summary: str
