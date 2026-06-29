import time
from typing import Dict, Any, List

class MiddlewareContext:
    """
    Context scoped strictly to the middleware pipeline execution.
    """
    def __init__(self):
        self.start_time_ms: int = int(time.time() * 1000)
        self.metadata: Dict[str, Any] = {}
        self.trace_data: Dict[str, Any] = {}
        self.policy_decisions: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
        self.warnings: List[str] = []
        
    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
