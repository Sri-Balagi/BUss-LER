"""Memory summarization prompt templates."""

from app.infrastructure.ai.prompts.template import PromptTemplate

memory_summarization_v1 = PromptTemplate(
    prompt_id="memory_summarization",
    version="v1",
    base_template=(
        "Summarize the following memory in one clear, concise sentence.\n"
        "Do not include commentary.\n\n"
        "Memory content:\n"
        "{memory_content}"
    ),
    context_variables=["memory_content"],
    metadata={"capability": "memory", "author": "BizOS Core"},
)
