"""
Resource Management Engine & Broker Subsystem for BizOS.
Handles allocation, reservations, rate limiting, token budgets, and cost accounting.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from app.shared.enums import ExecutionMode

class ResourceCategory(StrEnum):
    AGENT = "AGENT"
    LLM_TOKEN = "LLM_TOKEN"
    CONNECTOR = "CONNECTOR"
    WORKFLOW = "WORKFLOW"
    MEMORY = "MEMORY"

class AllocationPolicy(StrEnum):
    FAIR = "FAIR"
    PRIORITY = "PRIORITY"
    WEIGHTED = "WEIGHTED"
    RESERVED = "RESERVED"

class ResourceRequest(BaseModel):
    request_id: str
    category: ResourceCategory
    amount: float
    priority: int = 1 # Higher = more urgent
    tenant_id: str = "default"
    goal_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    connector_id: Optional[str] = None

class AllocationResult(BaseModel):
    request_id: str
    granted: bool
    amount_granted: float
    reason: str = "Success"
    allocated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CostRecord(BaseModel):
    cost_id: str = Field(default_factory=lambda: f"cost_{int(datetime.now(timezone.utc).timestamp()*1000)}")
    tenant_id: str = "default"
    goal_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    connector_id: Optional[str] = None
    category: ResourceCategory
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CostAccountingEngine:
    """Tracks platform usage costs aggregated per Goal, Workflow, Agent, Connector, and Tenant."""

    def __init__(self) -> None:
        self._records: List[CostRecord] = []
        self._token_cost_per_1k: float = 0.00015 # Gemini Flash rate
        self._embedding_cost_per_1k: float = 0.00002

    def record_llm_cost(
        self,
        tokens: int,
        tenant_id: str = "default",
        goal_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> CostRecord:
        cost_usd = (tokens / 1000.0) * self._token_cost_per_1k
        rec = CostRecord(
            tenant_id=tenant_id,
            goal_id=goal_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            category=ResourceCategory.LLM_TOKEN,
            tokens_used=tokens,
            estimated_cost_usd=round(cost_usd, 6),
        )
        self._records.append(rec)
        return rec

    def get_total_cost(self, tenant_id: Optional[str] = None, goal_id: Optional[str] = None) -> float:
        total = 0.0
        for r in self._records:
            if tenant_id and r.tenant_id != tenant_id:
                continue
            if goal_id and r.goal_id != goal_id:
                continue
            total += r.estimated_cost_usd
        return round(total, 6)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_records": len(self._records),
            "total_cost_usd": round(sum(r.estimated_cost_usd for r in self._records), 6),
            "total_tokens": sum(r.tokens_used for r in self._records),
        }

class ResourceBroker:
    """
    Centralized runtime arbitration layer between platform components and Resource Manager.
    Handles allocation, reservation, release, priority arbitration, and preemption.
    """

    def __init__(self, policy: AllocationPolicy = AllocationPolicy.PRIORITY) -> None:
        self._policy = policy
        self._active_allocations: Dict[str, ResourceRequest] = {}
        self._cost_engine = CostAccountingEngine()
        self._lock = asyncio.Lock()
        
        # Default capacity limits
        self._limits: Dict[ResourceCategory, float] = {
            ResourceCategory.AGENT: 100.0,      # Max 100 concurrent agents
            ResourceCategory.LLM_TOKEN: 1000000.0, # 1M tokens/min
            ResourceCategory.CONNECTOR: 50.0,   # Max 50 req/sec
            ResourceCategory.WORKFLOW: 30.0,    # Max 30 concurrent workflows
            ResourceCategory.MEMORY: 1024.0,    # 1GB memory pool
        }
        self._used: Dict[ResourceCategory, float] = {cat: 0.0 for cat in ResourceCategory}

    async def request_allocation(self, req: ResourceRequest, mode: ExecutionMode = ExecutionMode.PRODUCTION) -> AllocationResult:
        async with self._lock:
            # In SIMULATION or DRY_RUN mode, grant all allocations with 0 cost impact
            if mode in (ExecutionMode.SIMULATION, ExecutionMode.DRY_RUN):
                return AllocationResult(request_id=req.request_id, granted=True, amount_granted=req.amount, reason=f"Granted ({mode.value} mode)")

            current_used = self._used.get(req.category, 0.0)
            capacity = self._limits.get(req.category, 1000.0)

            if current_used + req.amount <= capacity:
                self._used[req.category] = current_used + req.amount
                self._active_allocations[req.request_id] = req
                return AllocationResult(request_id=req.request_id, granted=True, amount_granted=req.amount)
            else:
                return AllocationResult(
                    request_id=req.request_id,
                    granted=False,
                    amount_granted=0.0,
                    reason=f"Capacity exceeded for {req.category.value} (Used: {current_used}/{capacity})"
                )

    async def release_allocation(self, request_id: str) -> bool:
        async with self._lock:
            if request_id in self._active_allocations:
                req = self._active_allocations.pop(request_id)
                self._used[req.category] = max(0.0, self._used[req.category] - req.amount)
                return True
            return False

    @property
    def cost_engine(self) -> CostAccountingEngine:
        return self._cost_engine

    def get_status(self) -> Dict[str, Any]:
        return {
            "policy": self._policy.value,
            "limits": {k.value: v for k, v in self._limits.items()},
            "used": {k.value: v for k, v in self._used.items()},
            "active_allocations": len(self._active_allocations),
            "cost_summary": self._cost_engine.get_summary(),
        }
