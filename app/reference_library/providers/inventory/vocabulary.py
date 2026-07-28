from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_inventory_turnover', name='Inventory Turnover Ratio', description='The number of times inventory is sold or replaced in a year. Measures working capital efficiency in stock.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 33, 33891), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Turnover = COGS / Average Inventory Value'), SemanticTerm(artifact_id='term_eoq', name='Economic Order Quantity', description='Optimal order quantity that minimizes holding and ordering costs. Minimizes inventory replenishment expenses.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 33, 33891), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='EOQ = Sqrt((2 * Demand * OrderCost) / HoldingCost)')])
