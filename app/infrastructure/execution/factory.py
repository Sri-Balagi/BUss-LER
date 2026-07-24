
from app.domain.security.interfaces import IAuditPublisher
from app.infrastructure.execution.in_process import InProcessExecutionStrategy
from app.infrastructure.execution.sandboxed_strategy import SandboxedExecutionStrategy
from app.infrastructure.execution.strategy import ExecutionStrategy, IExecutionStrategy
from app.infrastructure.execution.subprocess_strategy import SubprocessExecutionStrategy


class ExecutionStrategyFactory:
    """Factory for creating execution strategies based on the strategy enum."""

    def __init__(self, audit_publisher: IAuditPublisher | None = None):
        self._audit_publisher = audit_publisher

    def get_strategy(self, strategy_type: ExecutionStrategy) -> IExecutionStrategy:
        """Return an instance of the requested execution strategy."""
        match strategy_type:
            case ExecutionStrategy.IN_PROCESS:
                return InProcessExecutionStrategy()
            case ExecutionStrategy.SUBPROCESS:
                return SubprocessExecutionStrategy()
            case ExecutionStrategy.SANDBOXED:
                return SandboxedExecutionStrategy(audit_publisher=self._audit_publisher)
            case _:
                raise NotImplementedError(f"Strategy {strategy_type} is not implemented.")
