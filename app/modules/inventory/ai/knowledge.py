"""Inventory AI Knowledge Pack re-exporting INVENTORY_KNOWLEDGE_MODEL with backward compatibility."""

from app.core.modules.ai.knowledge import DomainVocabulary, ModuleKnowledgePack
from app.modules.inventory.ai.cognition import INVENTORY_KNOWLEDGE_MODEL

INVENTORY_KNOWLEDGE_PACK = ModuleKnowledgePack(
    module_id=INVENTORY_KNOWLEDGE_MODEL.module_id,
    vocabularies=[
        DomainVocabulary(term=t.name, definition=t.description, aliases=[], formula=t.formula)
        for t in INVENTORY_KNOWLEDGE_MODEL.vocabulary.terms
    ],
    prompt_templates=[],
    reasoning_rules=[]
)
