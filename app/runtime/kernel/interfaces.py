from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

class IKernel(ABC):
    """The root Kernel abstraction for BizOS."""
    pass # Marker interface for DI

class IProcessManager(ABC):
    """Manages Process Control Blocks (PCBs) and the Process Table."""
    @abstractmethod
    def spawn(self, pcb: Any) -> None:
        pass

    @abstractmethod
    def terminate(self, pid: UUID) -> None:
        pass

    @abstractmethod
    def get_status(self, pid: UUID) -> Optional[Any]:
        pass

class IRuntimeManager(ABC):
    """Orchestrates the global state of OS compute resources."""
    @abstractmethod
    def start_runtime(self) -> None:
        pass

    @abstractmethod
    def shutdown_runtime(self) -> None:
        pass

class ISessionManager(ABC):
    """Manages Cognitive Sessions and their state lifecycle."""
    @abstractmethod
    def create_session(self, tenant_id: UUID) -> UUID:
        pass

class IScheduler(ABC):
    """Determines when and how tasks execute."""
    @abstractmethod
    def schedule(self, pcb: Any) -> None:
        pass

class IResourceManager(ABC):
    """Allocates compute, tokens, and budget."""
    @abstractmethod
    def allocate(self, resource_id: str, amount: float) -> bool:
        pass

    @abstractmethod
    def release(self, resource_id: str, amount: float) -> None:
        pass

class IPolicyEngine(ABC):
    """Declarative rules governing execution constraints and RBAC."""
    @abstractmethod
    def check_permission(self, subject: UUID, action: str, resource: str) -> bool:
        pass

class IServiceDiscovery(ABC):
    """Manages discovery of Agents, Capabilities, Tools, Plugins, and Domain Packs."""
    @abstractmethod
    def discover(self, service_type: str) -> List[Any]:
        pass
