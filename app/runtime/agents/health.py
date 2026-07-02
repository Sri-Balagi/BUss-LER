from pydantic import BaseModel, Field


class AgentHealth(BaseModel):
    """
    Passive health metrics tracked by the AgentHealthMonitor.
    Used by the Registry for ranking and capability resolution.
    """

    success_rate: float = Field(
        default=1.0, description="Ratio of successful executions (0.0 to 1.0)"
    )
    average_latency_ms: float = Field(
        default=0.0, description="Average execution duration in milliseconds"
    )
    recent_failures: int = Field(default=0, description="Count of recent consecutive failures")
    is_available: bool = Field(
        default=True, description="Whether the agent is currently available to accept work"
    )
    in_cooldown: bool = Field(
        default=False, description="Whether the agent is in a cooldown penalty state"
    )
