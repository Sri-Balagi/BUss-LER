"""Intent classification prompt templates."""

from app.infrastructure.ai.prompts.template import PromptTemplate

intent_classification_v1 = PromptTemplate(
    prompt_id="intent_classification",
    version="v1",
    base_template=(
        "You are an expert business intent classifier for an AI Operating System.\n\n"
        "Analyse the following user input and return a JSON object matching the schema below.\n"
        "Return ONLY the JSON object. No preamble, no explanation, no markdown.\n\n"
        "User input:\n"
        "{content}\n\n"
        "Business context (may be empty):\n"
        "{business_context}\n\n"
        "Required JSON schema:\n"
        "{{\n"
        '  "intent_type": "<one of: inventory, calendar, analytics, finance, communication, task_management, reporting, research, general>",\n'
        "  \"business_domain\": \"<short domain label, e.g. 'Supply Chain', 'Human Resources'>\",\n"
        '  "entities": [\n'
        '    {{"type": "<entity type>", "value": "<raw value>", "normalized": "<normalised form>"}}\n'
        "  ],\n"
        '  "related_goals": ["<goal category or title>"],\n'
        '  "urgency": "<low|normal|high|critical>",\n'
        '  "priority": <integer 1-10>,\n'
        '  "timeframe": "<natural language timeframe or null>",\n'
        '  "confidence": "<high|medium|low>",\n'
        '  "ambiguities": ["<ambiguous aspect>"],\n'
        '  "follow_up_questions": ["<clarifying question>"],\n'
        '  "reasoning_metadata": {{\n'
        '    "key_signals": ["<signal 1>"],\n'
        '    "classifier_notes": "<brief engineering note>"\n'
        "  }}\n"
        "}}"
    ),
    context_variables=["content", "business_context"],
    metadata={"capability": "intent", "author": "BizOS Core"},
)
