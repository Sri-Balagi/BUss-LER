import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

from app.domain.goals.models import Goal, GoalState
from app.domain.observation.models import ObservationResult
from app.application.agents.services.goal_lifecycle import (
    GoalLifecycleService,
    ReasoningService,
    PlanningService,
    WorkflowService,
    ObservationService,
    ReplanningService,
)
from app.application.observation.engine import ObservationEngine
from app.application.agents.runtime import AgentRuntime
from app.intelligence.executive.workflow import (
    Workflow,
    WorkflowTask,
    WorkflowResult,
    LocalDAGWorkflowEngine,
)


@pytest.mark.asyncio
async def test_goal_lifecycle_service():
    service = GoalLifecycleService()
    goal = await service.create_goal("Test Goal", "Description", "owner-1")
    assert goal.state == GoalState.CREATED
    assert len(goal.history) == 0

    goal = await service.update_state(goal, GoalState.REASONING)
    assert goal.state == GoalState.REASONING
    assert len(goal.history) == 1
    assert "REASONING" in goal.history[0]


@pytest.mark.asyncio
async def test_reasoning_and_planning_services():
    goal = Goal(title="Forecast Sales", description="Q4 sales", owner="sales-mgr")
    reasoning = ReasoningService()
    reasoning_out = await reasoning.reason(goal)
    assert "recommended_capabilities" in reasoning_out
    assert reasoning_out["goal_id"] == str(goal.goal_id)

    planning = PlanningService()
    wf = await planning.plan(goal, reasoning_out)
    assert len(wf.tasks) == 1
    task = next(iter(wf.tasks.values()))
    assert task.capability_id == "general_execution"


@pytest.mark.asyncio
async def test_observation_and_replanning_services():
    goal = Goal(title="Test", description="Test desc", owner="owner")
    obs_engine = ObservationEngine()
    obs_service = ObservationService(obs_engine)

    # Test success observation
    success_wf_result = WorkflowResult(success=True, task_results={uuid4(): "ok"})
    obs_res = await obs_service.observe(success_wf_result, goal)
    assert obs_res.goal_progress == 1.0
    assert obs_res.should_replan is False

    # Test failure observation & replanning
    failed_id = uuid4()
    failed_wf_result = WorkflowResult(success=False, task_results={}, failed_tasks=[failed_id])
    obs_fail = await obs_service.observe(failed_wf_result, goal)
    assert obs_fail.should_replan is True
    assert "failed_tasks_count" in obs_fail.metrics

    planning_svc = PlanningService()
    replanning_svc = ReplanningService(planning_svc)

    wf = Workflow()
    failed_task = WorkflowTask(capability_id="cap-1", payload={"foo": "bar"}, task_id=failed_id)
    failed_task.state = "FAILED"
    wf.tasks[failed_id] = failed_task

    replanned_wf = await replanning_svc.replan(goal, obs_fail, wf, max_iterations=5, current_iteration=1)
    assert replanned_wf is not None
    assert len(replanned_wf.tasks) == 1


@pytest.mark.asyncio
async def test_agent_runtime_execute_goal_closed_loop():
    mock_registry = MagicMock()
    mock_agent = MagicMock()
    mock_registry.get_agent.side_effect = lambda agent_id: mock_agent

    mock_wf_service = AsyncMock()
    mock_wf_service.execute_workflow.return_value = WorkflowResult(success=True, task_results={})

    runtime = AgentRuntime(
        event_bus=MagicMock(),
        registry=mock_registry,
        task_repo=MagicMock(),
        session_repo=MagicMock(),
        workflow_service=mock_wf_service,
    )

    res = await runtime.execute_goal("agent-123", "Generate financial report")
    assert res["status"] == "COMPLETED"
    assert res["state"] == "COMPLETED"
    assert res["agent_id"] == "agent-123"
    assert "REASONING" in "".join(res["history"])
    assert "PLANNING" in "".join(res["history"])
    assert "EXECUTING" in "".join(res["history"])
