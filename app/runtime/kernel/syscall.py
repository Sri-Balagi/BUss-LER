from enum import IntEnum
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID

class KernelRing(IntEnum):
    RING_0 = 0  # Core Kernel (Scheduler, ProcessManager, RuntimeManager)
    RING_1 = 1  # OS Services (WorkflowEngine, System Bus, Registry)
    RING_2 = 2  # System Plugins (Market-verified Domain Packs)
    RING_3 = 3  # User Applications (Untrusted Agents, Capabilities)

class ISyscallInterface(ABC):
    """
    The exact boundaries where untrusted code (agents/plugins in Ring 2/3) 
    requests privileges from the OS Kernel.
    """
    
    @abstractmethod
    def start_session(self, context: Dict[str, Any]) -> UUID:
        pass
        
    @abstractmethod
    def stop_session(self, session_id: UUID) -> None:
        pass
        
    @abstractmethod
    def suspend(self, pid: UUID) -> None:
        pass
        
    @abstractmethod
    def resume(self, pid: UUID) -> None:
        pass
        
    @abstractmethod
    def allocate(self, resource_type: str, amount: int) -> bool:
        pass
        
    @abstractmethod
    def release(self, resource_type: str, amount: int) -> None:
        pass
        
    @abstractmethod
    def read(self, uri: str) -> Any:
        pass
        
    @abstractmethod
    def write(self, uri: str, content: Any) -> None:
        pass
        
    @abstractmethod
    def search(self, query: str, context: Optional[str] = None) -> Any:
        pass
        
    @abstractmethod
    def invoke_capability(self, capability_uri: str, payload: Dict[str, Any]) -> Any:
        pass
        
    @abstractmethod
    def request_approval(self, approval_type: str, context: Dict[str, Any]) -> bool:
        pass
        
    @abstractmethod
    def publish_event(self, topic: str, event_data: Dict[str, Any]) -> None:
        pass
        
    @abstractmethod
    def subscribe(self, topic: str, callback: Any) -> None:
        pass
        
    @abstractmethod
    def log(self, level: str, message: str) -> None:
        pass
        
    @abstractmethod
    def checkpoint(self, pid: UUID) -> str:
        pass
        
    @abstractmethod
    def restore(self, pid: UUID, checkpoint_uri: str) -> bool:
        pass
