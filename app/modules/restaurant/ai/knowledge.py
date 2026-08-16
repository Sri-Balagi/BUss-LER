"""Restaurant AI Knowledge Pack re-exporting RESTAURANT_KNOWLEDGE_MODEL with backward compatibility."""

from app.core.modules.ai.knowledge import DomainVocabulary, ModuleKnowledgePack
from app.modules.restaurant.ai.cognition import RESTAURANT_KNOWLEDGE_MODEL

RESTAURANT_KNOWLEDGE_PACK = ModuleKnowledgePack(
    module_id=RESTAURANT_KNOWLEDGE_MODEL.module_id,
    vocabularies=[
        DomainVocabulary(term=t.name, definition=t.description, aliases=[], formula=t.formula)
        for t in RESTAURANT_KNOWLEDGE_MODEL.vocabulary.terms
    ],
    prompt_templates=[],
    reasoning_rules=[]
)
