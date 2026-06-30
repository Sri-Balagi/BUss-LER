"""Recommendation generation prompt templates."""

from app.infrastructure.ai.prompts.template import PromptTemplate

recommendation_generation_v1 = PromptTemplate(
    prompt_id="recommendation_generation",
    version="v1",
    base_template=(
        "You are a proactive AI advisor for an AI Operating System.\n\n"
        "Analyse the context below and generate actionable business recommendations.\n"
        "Return ONLY a JSON array. No preamble, no markdown.\n\n"
        "Current intent:\n"
        "{intent_context}\n\n"
        "Active goals:\n"
        "{goals_context}\n\n"
        "Relevant memories:\n"
        "{memory_context}\n\n"
        "Conversation history:\n"
        "{conversation_context}\n\n"
        "Business state:\n"
        "{business_state}\n\n"
        "Twin profile:\n"
        "{twin_context}\n\n"
        "Each recommendation must follow this schema:\n"
        "{{\n"
        '  "title": "<short title>",\n'
        '  "body": "<full recommendation text>",\n'
        '  "rationale": "<why this is recommended>",\n'
        '  "confidence": "<high|medium|low>",\n'
        '  "supporting_memory_refs": [<indices into provided memories>],\n'
        '  "supporting_goal_refs": [<indices into provided goals>],\n'
        '  "explainability_note": "<brief engineering note for observability>"\n'
        "}}\n\n"
        "Return a JSON array of 1-5 recommendations ordered by priority descending."
    ),
    context_variables=[
        "intent_context",
        "goals_context",
        "memory_context",
        "conversation_context",
        "business_state",
        "twin_context",
    ],
    metadata={"capability": "recommendation", "author": "BizOS Core"}
)
