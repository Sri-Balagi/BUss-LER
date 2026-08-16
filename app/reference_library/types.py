from typing import Protocol
from app.core.modules.ai.cognition import BusinessKnowledgeModel

class ReferenceProvider(Protocol):
    def build(self) -> BusinessKnowledgeModel:
        ...
