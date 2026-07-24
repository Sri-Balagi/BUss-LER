from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessType(StrEnum):
    APPLICATION = "APPLICATION"
    WORKFLOW = "WORKFLOW"
    AGENT = "AGENT"
    CAPABILITY = "CAPABILITY"
    SYSTEM = "SYSTEM"

class ProcessState(StrEnum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class ProcessControlBlock(BaseModel):
    """
    Tracks the state, memory pointers, and capabilities of an active task,
    workflow, or agent in the OS.
    """
    pid: UUID
    process_type: ProcessType
    state: ProcessState = ProcessState.CREATED
    parent_pid: UUID | None = None

    # Memory and Capabilities Pointers
    memory_pointers: dict[str, str] = Field(default_factory=dict)
    approved_syscalls: list[str] = Field(default_factory=list)

class ProcessTable:
    """
    In-memory tracker for all active processes in the Runtime Manager.
    """
    def __init__(self) -> None:
        self._processes: dict[UUID, ProcessControlBlock] = {}

    def register_process(self, pcb: ProcessControlBlock) -> None:
        self._processes[pcb.pid] = pcb

    def get_process(self, pid: UUID) -> ProcessControlBlock | None:
        return self._processes.get(pid)

    def remove_process(self, pid: UUID) -> None:
        if pid in self._processes:
            del self._processes[pid]

    def update_state(self, pid: UUID, new_state: ProcessState) -> None:
        if pid in self._processes:
            self._processes[pid].state = new_state
