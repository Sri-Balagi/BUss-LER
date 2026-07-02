from app.infrastructure.execution.in_process import InProcessExecutionStrategy
from app.infrastructure.execution.strategy import ExecutionStrategy, IExecutionStrategy
from app.infrastructure.execution.subprocess_strategy import SubprocessExecutionStrategy


class ExecutionStrategyFactory:
    """Factory for creating execution strategies based on the strategy enum."""

    @staticmethod
    def get_strategy(strategy_type: ExecutionStrategy) -> IExecutionStrategy:
        """Return an instance of the requested execution strategy."""
        match strategy_type:
            case ExecutionStrategy.IN_PROCESS:
                return InProcessExecutionStrategy()
            case ExecutionStrategy.SUBPROCESS:
                return SubprocessExecutionStrategy()
            case _:
                raise NotImplementedError(f"Strategy {strategy_type} is not implemented.")
