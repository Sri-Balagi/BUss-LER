from abc import ABC


class PromptTemplate(ABC):
    """Base for all prompt templates."""
    def __init__(self, template_str: str):
        self.template_str = template_str

    def render(self, **kwargs) -> str:
        return self.template_str.format(**kwargs)

class SystemPrompt(PromptTemplate):
    pass

class TaskPrompt(PromptTemplate):
    pass

class ContextPrompt(PromptTemplate):
    pass

class OutputSchemaPrompt(PromptTemplate):
    pass
