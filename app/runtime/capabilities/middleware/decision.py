from enum import Enum, auto


class MiddlewareDecision(Enum):
    """
    Determines the execution path after a middleware completes.
    """

    ALLOW = auto()  # Proceed to the next middleware or capability
    DENY = auto()  # Immediately reject execution
    SHORT_CIRCUIT = auto()  # Immediately return a success result (e.g., from cache)
    RETRY = auto()  # Retry the pipeline execution
