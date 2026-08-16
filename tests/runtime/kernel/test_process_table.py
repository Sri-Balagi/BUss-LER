from uuid import uuid4

import pytest

from app.runtime.kernel.process import ProcessControlBlock, ProcessState, ProcessTable, ProcessType


def test_process_table_registration():
    table = ProcessTable()
    pid = uuid4()
    pcb = ProcessControlBlock(pid=pid, process_type=ProcessType.AGENT)

    table.register_process(pcb)

    retrieved = table.get_process(pid)
    assert retrieved is not None
    assert retrieved.pid == pid
    assert retrieved.process_type == ProcessType.AGENT
    assert retrieved.state == ProcessState.CREATED

def test_process_table_update_state():
    table = ProcessTable()
    pid = uuid4()
    pcb = ProcessControlBlock(pid=pid, process_type=ProcessType.WORKFLOW)
    table.register_process(pcb)

    table.update_state(pid, ProcessState.RUNNING)

    retrieved = table.get_process(pid)
    assert retrieved.state == ProcessState.RUNNING

def test_process_table_removal():
    table = ProcessTable()
    pid = uuid4()
    pcb = ProcessControlBlock(pid=pid, process_type=ProcessType.CAPABILITY)
    table.register_process(pcb)

    table.remove_process(pid)

    assert table.get_process(pid) is None
