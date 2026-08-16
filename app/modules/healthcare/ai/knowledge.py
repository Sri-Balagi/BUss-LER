"""Healthcare AI Knowledge Pack re-exporting HEALTHCARE_KNOWLEDGE_MODEL with backward compatibility."""

from app.core.modules.ai.knowledge import DomainVocabulary, ModuleKnowledgePack
from app.modules.healthcare.ai.cognition import HEALTHCARE_KNOWLEDGE_MODEL

HEALTHCARE_KNOWLEDGE_PACK = ModuleKnowledgePack(
    module_id=HEALTHCARE_KNOWLEDGE_MODEL.module_id,
    vocabularies=[
        DomainVocabulary(term=t.name, definition=t.description, aliases=[], formula=t.formula)
        for t in HEALTHCARE_KNOWLEDGE_MODEL.vocabulary.terms
    ],
    prompt_templates=[],
    reasoning_rules=[]
)
