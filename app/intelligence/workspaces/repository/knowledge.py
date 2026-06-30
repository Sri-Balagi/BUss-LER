from typing import Any, Dict


class StrategicKnowledge:
    def __init__(self, k_id: str, content: Any, category: str):
        self.k_id = k_id
        self.content = content
        self.category = category # e.g. "Lesson", "Heuristic"

class ExecutiveKnowledgeRepository:
    """
    Stores long-term strategic insights, historical strategy performance, and executive preferences.
    Differentiates strategic knowledge from factual memory.
    """
    def __init__(self):
        self.knowledge_base: dict[str, StrategicKnowledge] = {}

    def store_knowledge(self, knowledge: StrategicKnowledge):
        self.knowledge_base[knowledge.k_id] = knowledge

    def retrieve_knowledge(self, k_id: str) -> StrategicKnowledge:
        return self.knowledge_base.get(k_id)
