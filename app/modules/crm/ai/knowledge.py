"""CRM AI Knowledge Pack re-exporting CRM_KNOWLEDGE_MODEL with backward compatibility."""

from app.core.modules.ai.knowledge import DomainVocabulary, ModuleKnowledgePack
from app.modules.crm.ai.cognition import CRM_KNOWLEDGE_MODEL

CRM_KNOWLEDGE_PACK = ModuleKnowledgePack(
    module_id=CRM_KNOWLEDGE_MODEL.module_id,
    vocabularies=[
        DomainVocabulary(term=t.name, definition=t.description, aliases=[], formula=t.formula)
        for t in CRM_KNOWLEDGE_MODEL.vocabulary.terms
    ],
    prompt_templates=[],
    reasoning_rules=[]
)
