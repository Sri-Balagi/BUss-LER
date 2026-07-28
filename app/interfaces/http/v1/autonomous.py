"""Autonomous AI Operating System REST API Router — Wave 6 Complete.

Exposes closed-loop autonomous goal execution, DAG workflow inspection,
human-in-the-loop checkpoint resumption, and module agent template discovery.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.shared.enums import AgentCapability
from app.application.agents.registry import InMemoryAgentRegistry
from app.application.agents.runtime import AgentRuntime
from app.core.modules.registry import get_module_registry
from app.domain.agents.models import Agent
from app.domain.workflows.repository import IWorkflowRepository
from app.infrastructure.persistence.workflow_repository import InMemoryWorkflowRepository
from app.intelligence.executive.workflow import LocalDAGWorkflowEngine

router = APIRouter(prefix="/autonomous", tags=["Autonomous AI OS"])


# ── Pydantic Request & Response Models ──────────────────────────────────────


class ExecuteGoalRequest(BaseModel):
    agent_id: str = Field(..., description="ID of the agent to assign the goal to")
    goal_description: str = Field(..., description="Description of the strategic goal")
    module_name: Optional[str] = Field(None, description="Optional domain module context")


class ExecuteGoalResponse(BaseModel):
    status: str
    agent_id: str
    goal: str
    goal_id: Optional[str] = None
    state: Optional[str] = None
    history: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)


class ResumeCheckpointRequest(BaseModel):
    checkpoint_state: str = Field(..., description="State to resume checkpoint with (e.g., APPROVED, REJECTED)")
    session_id: str = Field(default="default-session", description="Session ID for execution context")


class AgentTemplateResponse(BaseModel):
    template_id: str
    name: str
    role: str
    description: str
    capabilities: list[str]
    default_permissions: list[str]
    default_workflows: list[str]


class InstantiateAgentRequest(BaseModel):
    template_id: str = Field(..., description="Template ID to instantiate from")
    override_name: Optional[str] = Field(None, description="Optional custom name for the instantiated agent")


# ── Singleton Helpers for API Layer ─────────────────────────────────────────

_default_workflow_repo: Optional[IWorkflowRepository] = None
_default_engine: Optional[LocalDAGWorkflowEngine] = None
_default_runtime: Optional[AgentRuntime] = None


def get_workflow_repository() -> IWorkflowRepository:
    global _default_workflow_repo
    if _default_workflow_repo is None:
        _default_workflow_repo = InMemoryWorkflowRepository()
    return _default_workflow_repo


def get_workflow_engine() -> LocalDAGWorkflowEngine:
    global _default_engine
    if _default_engine is None:
        repo = get_workflow_repository()
        _default_engine = LocalDAGWorkflowEngine(workflow_repository=repo)
    return _default_engine


def get_agent_runtime() -> AgentRuntime:
    global _default_runtime
    if _default_runtime is None:
        registry = InMemoryAgentRegistry()
        registry.register_agent(
            Agent(
                id="agent-1",
                name="Default Autonomous Agent",
                description="Default operating system executive agent",
                capabilities=[AgentCapability.EXECUTION, AgentCapability.REASONING, AgentCapability.PLANNING],
            )
        )
        engine = get_workflow_engine()
        _default_runtime = AgentRuntime(registry=registry, workflow_service=engine)
    return _default_runtime


# ── REST API Endpoints ──────────────────────────────────────────────────────


@router.post(
    "/goals/execute",
    response_model=ExecuteGoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute an Autonomous Goal",
    description="Submits an autonomous goal to AgentRuntime for reasoning, planning, parallel DAG execution, and observation.",
)
async def execute_goal_endpoint(
    request: ExecuteGoalRequest,
    runtime: AgentRuntime = Depends(get_agent_runtime),
) -> ExecuteGoalResponse:
    try:
        result = await runtime.execute_goal(request.agent_id, request.goal_description)
        return ExecuteGoalResponse(
            status=result.get("status", "unknown"),
            agent_id=result.get("agent_id", request.agent_id),
            goal=result.get("goal", request.goal_description),
            goal_id=result.get("goal_id"),
            state=result.get("state"),
            history=result.get("history", []),
            metrics=result.get("metrics", {}),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Goal execution failed: {exc}")


@router.get(
    "/workflows/{workflow_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Workflow Execution State",
    description="Retrieves a persisted workflow and its task states by workflow ID.",
)
async def get_workflow_endpoint(
    workflow_id: str,
    repo: IWorkflowRepository = Depends(get_workflow_repository),
) -> dict[str, Any]:
    wf = await repo.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found")

    tasks_info = {}
    for tid, task in wf.tasks.items():
        tasks_info[str(tid)] = {
            "capability_id": task.capability_id,
            "state": getattr(task.state, "value", str(task.state)),
            "payload": task.payload,
            "has_checkpoint": task.checkpoint is not None,
        }

    return {
        "workflow_id": str(wf.workflow_id),
        "version": wf.version,
        "tasks_count": len(wf.tasks),
        "tasks": tasks_info,
    }


@router.post(
    "/workflows/{workflow_id}/checkpoints/{task_id}/resume",
    status_code=status.HTTP_200_OK,
    summary="Resume a Paused Workflow Checkpoint",
    description="Resumes execution of a workflow paused at a human-in-the-loop checkpoint.",
)
async def resume_checkpoint_endpoint(
    workflow_id: str,
    task_id: str,
    request: ResumeCheckpointRequest,
    engine: LocalDAGWorkflowEngine = Depends(get_workflow_engine),
) -> dict[str, Any]:
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task UUID format")

    result = await engine.resume_checkpoint(
        workflow_id=workflow_id,
        task_id=task_uuid,
        checkpoint_state=request.checkpoint_state,
        session_id=request.session_id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not resume checkpoint for workflow {workflow_id} and task {task_id}",
        )

    return {
        "status": "resumed",
        "workflow_id": workflow_id,
        "task_id": task_id,
        "success": result.success,
        "checkpoint_state": request.checkpoint_state,
    }


@router.get(
    "/modules/{module_name}/agent-templates",
    response_model=list[AgentTemplateResponse],
    status_code=status.HTTP_200_OK,
    summary="List Module Agent Templates",
    description="Discovers all default AgentTemplate definitions from a specified business module.",
)
async def list_agent_templates_endpoint(
    module_name: str,
) -> list[AgentTemplateResponse]:
    registry = get_module_registry()
    module = registry.get(module_name.lower())
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_name}' not found in BizOS registry.",
        )

    if not hasattr(module, "list_agent_templates"):
        return []

    templates = module.list_agent_templates()
    response_items = []
    for t in templates:
        response_items.append(
            AgentTemplateResponse(
                template_id=t.template_id,
                name=t.name,
                role=t.role,
                description=t.description,
                capabilities=t.capabilities,
                default_permissions=t.default_permissions,
                default_workflows=t.default_workflows,
            )
        )
    return response_items
