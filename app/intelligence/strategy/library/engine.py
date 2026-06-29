from typing import List, Optional
from app.intelligence.strategy.library.models import StrategyDefinition, StrategyCatalog

class StrategyLibrary:
    """
    Maintains and categorizes reusable business strategies.
    """
    def __init__(self):
        self._catalog = [
            StrategyDefinition(strategy_id="STRAT_001", name="Cost Reduction", category="FINANCE", description="Reduce operational costs"),
            StrategyDefinition(strategy_id="STRAT_002", name="Market Expansion", category="GROWTH", description="Expand into new geographic markets"),
            StrategyDefinition(strategy_id="STRAT_003", name="Customer Retention", category="SERVICE", description="Increase retention through loyalty programs"),
        ]

    def get_catalog(self) -> StrategyCatalog:
        return StrategyCatalog(strategies=self._catalog)

    def retrieve_by_category(self, category: str) -> List[StrategyDefinition]:
        return [s for s in self._catalog if s.category == category]
