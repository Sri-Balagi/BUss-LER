from app.runtime.kernel.interfaces import IScheduler
from app.runtime.kernel.manager import ProcessManager
from app.runtime.kernel.process import ProcessControlBlock, ProcessState


class LocalScheduler(IScheduler):
    """
    In-memory task scheduler.
    In later milestones, this will be replaced by DistributedScheduler (Celery).
    """
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager

    def schedule(self, pcb: ProcessControlBlock) -> None:
        """Schedules a process for execution locally."""
        self.process_manager.spawn(pcb)
        self.process_manager.process_table.update_state(pcb.pid, ProcessState.READY)

        # Simulating immediate dispatch in a local environment
        self.process_manager.process_table.update_state(pcb.pid, ProcessState.RUNNING)
