from uuid import UUID

from app.runtime.kernel.interfaces import IProcessManager, IRuntimeManager
from app.runtime.kernel.process import ProcessControlBlock, ProcessState, ProcessTable
from app.shared.bus.system_bus import ISystemBus


class ProcessManager(IProcessManager):
    """
    Manages the lifecycle and tracking of Process Control Blocks within the in-memory ProcessTable.
    """
    def __init__(self, process_table: ProcessTable):
        self.process_table = process_table

    def spawn(self, pcb: ProcessControlBlock) -> None:
        self.process_table.register_process(pcb)

    def terminate(self, pid: UUID) -> None:
        self.process_table.update_state(pid, ProcessState.TERMINATED)

    def get_status(self, pid: UUID) -> ProcessState | None:
        pcb = self.process_table.get_process(pid)
        return pcb.state if pcb else None

class RuntimeManager(IRuntimeManager):
    """
    Orchestrates the global state of the OS compute resources.
    Uses the ProcessManager to track processes.
    """
    def __init__(self, process_manager: ProcessManager, system_bus: ISystemBus):
        self.process_manager = process_manager
        self.system_bus = system_bus
        self._is_running = False

    def start_runtime(self) -> None:
        self._is_running = True

        class OSReadyEvent:
            pass

        self.system_bus.publish_event(OSReadyEvent())

    def shutdown_runtime(self) -> None:
        self._is_running = False
