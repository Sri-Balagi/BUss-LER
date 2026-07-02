import time
from typing import Any


class MiddlewareContext:
    """
    Context scoped strictly to the middleware pipeline execution.
    """

    def __init__(self):
        self.start_time_ms: int = int(time.time() * 1000)
        self.metadata: dict[str, Any] = {}
        self.trace_data: dict[str, Any] = {}
        self.policy_decisions: dict[str, Any] = {}
        self.metrics: dict[str, Any] = {}
        self.warnings: list[str] = []

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
