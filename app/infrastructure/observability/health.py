from enum import Enum
from typing import Dict

class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"

class HealthMonitor:
    def __init__(self):
        self.services = {
            "MemoryPlatform": HealthStatus.HEALTHY,
            "DecisionPlatform": HealthStatus.HEALTHY,
            "IntelligencePlatform": HealthStatus.HEALTHY,
            "EventBus": HealthStatus.HEALTHY,
            "RepositoryLayer": HealthStatus.HEALTHY
        }
    
    def check_liveness(self) -> bool:
        return True
        
    def check_readiness(self) -> bool:
        return all(status != HealthStatus.UNHEALTHY for status in self.services.values())
        
    def get_dependency_health(self) -> Dict[str, HealthStatus]:
        return self.services.copy()

    def set_service_health(self, service_name: str, status: HealthStatus):
        if service_name in self.services:
            self.services[service_name] = status
