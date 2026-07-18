import abc
from typing import Dict, Any, Optional

from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.prompt.models import PromptTemplate

class IPromptBuilder(abc.ABC):
    """Builder to orchestrate and format prompts."""
    
    @abc.abstractmethod
    async def build(self, template: PromptTemplate, context: ApplicationContext, additional_vars: Optional[Dict[str, Any]] = None) -> str:
        """Build a formatted prompt string from template and context."""
        pass
