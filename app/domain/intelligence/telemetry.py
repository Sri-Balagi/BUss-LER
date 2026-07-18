from pydantic import BaseModel, Field

class IntelligenceMetrics(BaseModel):
    """
    Standardized metrics payload for all intelligence operations.
    Enables unified dashboards and tracing without subsystems inventing their own formats.
    """
    execution_time_ms: float = Field(default=0.0)
    provider_time_ms: float = Field(default=0.0)
    overhead_time_ms: float = Field(default=0.0)
    
    # Optional dimension counts
    tokens_consumed: int = Field(default=0)
    candidates_evaluated: int = Field(default=0)
    
    # Generic error tracking
    error_count: int = Field(default=0)
    
    class Config:
        frozen = True
