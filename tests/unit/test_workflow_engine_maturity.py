import asyncio
import pytest
from uuid import uuid4

from app.domain.workflows.models import (
    ConditionExpression,
    ConditionOperator,
    ApprovalCheckpoint,
    ReviewCheckpoint,
    WaitCheckpoint,
    ExternalEventCheckpoint,
    WorkflowExecutionContext,
)
from app.domain.workflows.repository import IWorkflowRepository
from app.infrastructure.persistence.workflow_repository import InMemoryWorkflowRepository
from app.intelligence.executive.workflow import (
    Workflow,
    WorkflowTask,
    TaskState,
    LocalDAGWorkflowEngine,
)
from app.runtime.agents.capability import Capability
from app.runtime.agents.registry import ResolutionContext


@pytest.mark.asyncio
async def test_condition_expression_evaluations():
    ctx = {"role": "admin", "score": 85, "tags": ["sales", "enterprise"]}

    cond_eq = ConditionExpression(field="role", operator=ConditionOperator.EQ, value="admin")
    assert cond_eq.evaluate(ctx) is True

    cond_gt = ConditionExpression(field="score", operator=ConditionOperator.GT, value=80)
    assert cond_gt.evaluate(ctx) is True

    cond_contains = ConditionExpression(field="tags", operator=ConditionOperator.CONTAINS, value="sales")
    assert cond_contains.evaluate(ctx) is True

    cond_exists = ConditionExpression(field="role", operator=ConditionOperator.EXISTS)
    assert cond_exists.evaluate(ctx) is True


@pytest.mark.asyncio
async def test_checkpoint_hierarchy():
    approval = ApprovalCheckpoint(name="Manager Approval", required_role="manager")
    assert approval.checkpoint_type == "approval"
    assert approval.required_role == "manager"

    review = ReviewCheckpoint(name="Code Review", reviewer_role="tech_lead")
    assert review.checkpoint_type == "review"

    wait = WaitCheckpoint(name="Cooldown", duration_seconds=120)
    assert wait.duration_seconds == 120

    evt = ExternalEventCheckpoint(name="Webhook Received", event_name="payment_processed")
    assert evt.event_name == "payment_processed"


@pytest.mark.asyncio
async def test_in_memory_workflow_repository():
    repo: IWorkflowRepository = InMemoryWorkflowRepository()
    wf = Workflow(version="1.0.0")
    wf.execution_context = WorkflowExecutionContext(goal_id="goal-123")

    await repo.save_workflow(wf)
    loaded = await repo.get_workflow(str(wf.workflow_id))
    assert loaded is not None
    assert loaded.version == "1.0.0"
    assert loaded.execution_context.goal_id == "goal-123"

    by_goal = await repo.list_workflows_by_goal("goal-123")
    assert len(by_goal) == 1


class MockAgent:
    def __init__(self, output_val: str = "success") -> None:
        self.output_val = output_val

    async def execute(self):
        class Res:
            pass
        res = Res()
        res.output = self.output_val
        return res


class MockFactory:
    def create_agent(self, spec):
        return MockAgent()

    def release_agent(self, agent):
        pass


class MockRegistry:
    def resolve(self, context: ResolutionContext):
        class Res:
            pass
        res = Res()
        res.selected_factory = MockFactory()
        res.selected_specification = {}
        return res


@pytest.mark.asyncio
async def test_local_dag_engine_condition_skipping():
    registry = MockRegistry()
    engine = LocalDAGWorkflowEngine(capability_registry=registry)

    wf = Workflow()
    t1 = WorkflowTask(capability_id="cap1", payload={"foo": "bar"})
    t1.condition = lambda results: False
    wf.add_task(t1)

    result = await engine.execute_workflow(wf, session_id="test-session")
    assert result.success is True
    assert t1.state == TaskState.SKIPPED


@pytest.mark.asyncio
async def test_local_dag_engine_checkpoint_pausing_and_resuming():
    registry = MockRegistry()
    repo = InMemoryWorkflowRepository()
    engine = LocalDAGWorkflowEngine(capability_registry=registry, workflow_repository=repo)

    wf = Workflow()
    t1 = WorkflowTask(capability_id="cap1", payload={"foo": "bar"})
    t1.checkpoint = ApprovalCheckpoint(name="Need OK", required_role="admin")
    wf.add_task(t1)

    result = await engine.execute_workflow(wf, session_id="test-session")
    assert result.success is True
    assert t1.state == TaskState.WAITING_CHECKPOINT

    # Now resume the checkpoint
    resume_result = await engine.resume_checkpoint(
        workflow_id=str(wf.workflow_id),
        task_id=t1.task_id,
        checkpoint_state="APPROVED",
        session_id="test-session"
    )
    assert resume_result is not None
    assert resume_result.success is True
    assert t1.state == TaskState.COMPLETED
