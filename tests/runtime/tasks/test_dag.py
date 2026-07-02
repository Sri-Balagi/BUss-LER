from uuid import uuid4

import pytest

from app.runtime.tasks.dag import DAGValidationError, TaskDAG
from app.runtime.tasks.models import ExecutionDescriptor, ExecutionType, Task


def create_mock_task(task_id=None, deps=None):
    if not task_id:
        task_id = uuid4()
    if not deps:
        deps = set()

    desc = ExecutionDescriptor(execution_type=ExecutionType.SYSTEM, target="mock")
    return Task(id=task_id, execution_descriptor=desc, task_dependencies=deps)


def test_dag_validation_success():
    dag = TaskDAG()

    t1 = create_mock_task()
    t2 = create_mock_task(deps={t1.task_id})
    t3 = create_mock_task(deps={t1.task_id, t2.task_id})

    dag.add_task(t1)
    dag.add_task(t2)
    dag.add_task(t3)

    # Should not raise
    dag.validate()


def test_dag_missing_dependency():
    dag = TaskDAG()

    t1 = create_mock_task(deps={uuid4()})  # Missing dep
    dag.add_task(t1)

    with pytest.raises(DAGValidationError, match="missing task"):
        dag.validate()


def test_dag_cycle_detection():
    dag = TaskDAG()

    id1 = uuid4()
    id2 = uuid4()

    t1 = create_mock_task(task_id=id1, deps={id2})
    t2 = create_mock_task(task_id=id2, deps={id1})

    dag.add_task(t1)
    dag.add_task(t2)

    with pytest.raises(DAGValidationError, match="Cycle detected"):
        dag.validate()


def test_dag_topological_layers():
    dag = TaskDAG()

    t1 = create_mock_task()  # Layer 0
    t2 = create_mock_task()  # Layer 0

    t3 = create_mock_task(deps={t1.task_id})  # Layer 1
    t4 = create_mock_task(deps={t1.task_id, t2.task_id})  # Layer 1

    t5 = create_mock_task(deps={t3.task_id, t4.task_id})  # Layer 2

    for t in [t1, t2, t3, t4, t5]:
        dag.add_task(t)

    layers = dag.get_topological_layers()

    assert len(layers) == 3
    assert layers[0] == {t1.task_id, t2.task_id}
    assert layers[1] == {t3.task_id, t4.task_id}
    assert layers[2] == {t5.task_id}
