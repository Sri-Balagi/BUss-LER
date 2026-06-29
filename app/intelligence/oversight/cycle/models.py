from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class CycleStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    CONVERGED = "CONVERGED"
    MAX_ITERATIONS_REACHED = "MAX_ITERATIONS_REACHED"
    ABORTED = "ABORTED"

class CognitiveCycleState(BaseModel):
    """Tracks the iterations of the executive reasoning process."""
    cycle_id: str
    current_iteration: int = 0
    max_iterations: int = 5
    status: CycleStatus = CycleStatus.INITIALIZED
    history: List[str] = Field(default_factory=list)
