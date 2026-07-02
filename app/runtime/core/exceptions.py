from app.shared.exceptions.errors import BizOSError


class ExecutionError(BizOSError):
    """Base exception for all runtime execution errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, detail=str(details) if details else None)


class BudgetExceededError(ExecutionError):
    """Thrown when an execution budget (tokens, time, etc.) is exceeded."""

    def __init__(self, resource_type: str, limit: int, actual: int):
        super().__init__(
            message=f"Budget exceeded for {resource_type}. Limit: {limit}, Actual: {actual}",
            details={"resource_type": resource_type, "limit": limit, "actual": actual},
        )


class AgentSuspendedError(ExecutionError):
    """Thrown when an agent is suspended and cannot process tasks."""

    def __init__(self, agent_id: str, reason: str):
        super().__init__(
            message=f"Agent {agent_id} is suspended: {reason}",
            details={"agent_id": agent_id, "reason": reason},
        )


class InvalidStateTransitionError(ExecutionError):
    """Thrown when a state machine attempts an invalid transition."""

    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            message=f"Invalid state transition from {from_state} to {to_state}",
            details={"from_state": from_state, "to_state": to_state},
        )
