"""Accounting AI Knowledge Pack re-exporting ACCOUNTING_KNOWLEDGE_MODEL with backward compatibility."""

from app.core.modules.ai.knowledge import DomainVocabulary, ModuleKnowledgePack
from app.modules.accounting.ai.cognition import ACCOUNTING_KNOWLEDGE_MODEL

ACCOUNTING_KNOWLEDGE_PACK = ModuleKnowledgePack(
    module_id=ACCOUNTING_KNOWLEDGE_MODEL.module_id,
    vocabularies=[
        DomainVocabulary(term=t.name, definition=t.description, aliases=[], formula=t.formula)
        for t in ACCOUNTING_KNOWLEDGE_MODEL.vocabulary.terms
    ],
    prompt_templates=[],
    reasoning_rules=[]
)
