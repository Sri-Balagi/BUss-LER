from uuid import uuid4

from app.runtime.tasks.models import ExecutionDescriptor, ExecutionType, Task, TaskPriority


def test_execution_descriptor_creation():
    desc = ExecutionDescriptor(
        execution_type=ExecutionType.AGENT,
        target="ResearchCapability",
        parameters={"topic": "AI"},
        timeout_ms=5000,
        retries_allowed=3,
    )
    assert desc.execution_type == ExecutionType.AGENT
    assert desc.target == "ResearchCapability"
    assert desc.parameters["topic"] == "AI"
    assert desc.timeout_ms == 5000
    assert desc.retries_allowed == 3


def test_task_creation():
    desc = ExecutionDescriptor(execution_type=ExecutionType.TOOL, target="Calculator")
    dep_id = uuid4()

    task = Task(
        execution_descriptor=desc, task_dependencies={dep_id}, task_priority=TaskPriority.HIGH
    )

    assert task.task_id is not None
    assert task.descriptor == desc
    assert dep_id in task.dependencies
    assert task.priority == TaskPriority.HIGH
