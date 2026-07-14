import pytest
from app.runtime.kernel.process import ProcessState, ProcessType

def test_process_states_exist():
    assert hasattr(ProcessState, "CREATED")
    assert hasattr(ProcessState, "READY")
    assert hasattr(ProcessState, "RUNNING")
    assert hasattr(ProcessState, "WAITING")
    assert hasattr(ProcessState, "SUSPENDED")
    assert hasattr(ProcessState, "TERMINATED")
    assert hasattr(ProcessState, "FAILED")

def test_process_types_exist():
    assert hasattr(ProcessType, "APPLICATION")
    assert hasattr(ProcessType, "WORKFLOW")
    assert hasattr(ProcessType, "AGENT")
    assert hasattr(ProcessType, "CAPABILITY")
    assert hasattr(ProcessType, "SYSTEM")
