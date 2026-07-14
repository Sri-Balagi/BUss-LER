import pytest
from uuid import uuid4
from app.runtime.kernel.process import ProcessTable, ProcessControlBlock, ProcessType, ProcessState
from app.runtime.kernel.manager import ProcessManager, RuntimeManager

def test_process_manager_spawn_terminate():
    table = ProcessTable()
    manager = ProcessManager(table)
    
    pid = uuid4()
    pcb = ProcessControlBlock(pid=pid, process_type=ProcessType.AGENT)
    
    manager.spawn(pcb)
    assert manager.get_status(pid) == ProcessState.CREATED
    
    manager.terminate(pid)
    assert manager.get_status(pid) == ProcessState.TERMINATED

def test_runtime_manager_init():
    table = ProcessTable()
    p_manager = ProcessManager(table)
    r_manager = RuntimeManager(p_manager, None)
    
    assert r_manager.process_manager is p_manager
