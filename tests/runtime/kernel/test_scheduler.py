from uuid import uuid4

import pytest

from app.runtime.kernel.manager import ProcessManager
from app.runtime.kernel.process import ProcessControlBlock, ProcessState, ProcessTable, ProcessType
from app.runtime.kernel.scheduler import LocalScheduler


def test_local_scheduler():
    table = ProcessTable()
    manager = ProcessManager(table)
    scheduler = LocalScheduler(manager)

    pid = uuid4()
    pcb = ProcessControlBlock(pid=pid, process_type=ProcessType.WORKFLOW)

    scheduler.schedule(pcb)

    assert manager.get_status(pid) == ProcessState.RUNNING
