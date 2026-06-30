"""Goal planning prompt templates."""

from app.infrastructure.ai.prompts.template import PromptTemplate

goal_planning_v1 = PromptTemplate(
    prompt_id="goal_planning",
    version="v1",
    base_template=(
        "You are an expert business strategist and execution planner.\n\n"
        "Generate a structured execution plan for the goal described below.\n"
        "Return ONLY a JSON object matching the schema. No preamble, no markdown.\n\n"
        "Goal:\n"
        "{goal_title}\n\n"
        "Goal description:\n"
        "{goal_description}\n\n"
        "Current intent:\n"
        "{intent_context}\n\n"
        "Active goals (context):\n"
        "{goals_context}\n\n"
        "Relevant memories (context):\n"
        "{memory_context}\n\n"
        "Conversation history:\n"
        "{conversation_context}\n\n"
        "Business state:\n"
        "{business_state}\n\n"
        "Twin profile:\n"
        "{twin_context}\n\n"
        "Required JSON schema:\n"
        "{{\n"
        '  "rationale": "<why this plan addresses the goal>",\n'
        '  "steps": [\n'
        "    {{\n"
        '      "step_number": <int>,\n'
        '      "action": "<action description>",\n'
        '      "expected_outcome": "<expected result>",\n'
        '      "depends_on": [<step numbers>],\n'
        '      "estimated_effort": "<time estimate or null>"\n'
        "    }}\n"
        "  ],\n"
        '  "assumptions": ["<assumption>"],\n'
        '  "risks": [\n'
        '    {{"risk": "<risk description>", "likelihood": "<low|medium|high>", "mitigation": "<mitigation strategy>"}}\n'
        "  ],\n"
        '  "dependencies": ["<external dependency>"],\n'
        '  "estimated_effort": "<total effort estimate or null>",\n'
        '  "confidence": <float 0.0-1.0>\n'
        "}}"
    ),
    context_variables=[
        "goal_title",
        "goal_description",
        "intent_context",
        "goals_context",
        "memory_context",
        "conversation_context",
        "business_state",
        "twin_context",
    ],
    metadata={"capability": "planning", "author": "BizOS Core"}
)
