import pytest
from uuid import uuid4
from app.runtime.kernel.process import ProcessTable, ProcessState, ProcessControlBlock, ProcessType
from app.runtime.kernel.manager import ProcessManager
from app.runtime.lifecycle.session import SessionLifecycleManager
from app.runtime.lifecycle.workflow import WorkflowLifecycleManager
from app.runtime.lifecycle.process import ProcessLifecycleManager
from app.runtime.lifecycle.interfaces import InvalidStateTransitionError

def test_session_lifecycle():
    mgr = SessionLifecycleManager()
    uid = uuid4()
    assert mgr.get_state(uid) == "CREATED"
    mgr.transition(uid, "INITIALIZED")
    mgr.transition(uid, "RUNNING")
    assert mgr.get_state(uid) == "RUNNING"

def test_session_lifecycle_invalid_transition():
    mgr = SessionLifecycleManager()
    uid = uuid4()
    with pytest.raises(InvalidStateTransitionError):
        mgr.transition(uid, "COMPLETED")  # Cannot skip INITIALIZED -> RUNNING

def test_workflow_lifecycle():
    mgr = WorkflowLifecycleManager()
    uid = uuid4()
    assert mgr.get_state(uid) == "QUEUED"
    mgr.transition(uid, "SCHEDULED")
    mgr.transition(uid, "EXECUTING")
    assert mgr.get_state(uid) == "EXECUTING"

def test_workflow_lifecycle_invalid_transition():
    mgr = WorkflowLifecycleManager()
    uid = uuid4()
    with pytest.raises(InvalidStateTransitionError):
        mgr.transition(uid, "COMPLETED")  # Cannot skip QUEUED -> COMPLETED

def test_process_lifecycle():
    table = ProcessTable()
    p_mgr = ProcessManager(table)
    mgr = ProcessLifecycleManager(p_mgr)

    uid = uuid4()
    p_mgr.spawn(ProcessControlBlock(pid=uid, process_type=ProcessType.AGENT))
    assert mgr.get_state(uid) == ProcessState.CREATED
    mgr.transition(uid, ProcessState.READY)
    mgr.transition(uid, ProcessState.RUNNING)
    mgr.transition(uid, ProcessState.SUSPENDED)
    assert mgr.get_state(uid) == ProcessState.SUSPENDED

def test_process_lifecycle_invalid_transition():
    table = ProcessTable()
    p_mgr = ProcessManager(table)
    mgr = ProcessLifecycleManager(p_mgr)

    uid = uuid4()
    p_mgr.spawn(ProcessControlBlock(pid=uid, process_type=ProcessType.AGENT))
    with pytest.raises(InvalidStateTransitionError):
        mgr.transition(uid, ProcessState.RUNNING)  # Cannot skip CREATED -> RUNNING
