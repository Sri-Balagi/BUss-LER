from pydantic import BaseModel, Field
from typing import List

class StrategyDefinition(BaseModel):
    """A reusable business strategy from the catalog."""
    strategy_id: str
    name: str
    category: str
    description: str
    historical_success_rate: float = 0.0

class StrategyCatalog(BaseModel):
    """Collection of available strategies."""
    strategies: List[StrategyDefinition] = Field(default_factory=list)
