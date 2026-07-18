from typing import Dict, Any, Optional
from string import Template

from app.domain.applications.prompt.interfaces import IPromptBuilder
from app.domain.applications.prompt.models import PromptTemplate
from app.domain.applications.context.models import ApplicationContext

class PromptOrchestrationService(IPromptBuilder):
    async def build(self, template: PromptTemplate, context: ApplicationContext, additional_vars: Optional[Dict[str, Any]] = None) -> str:
        vars_dict = context.variables.copy()
        if additional_vars:
            vars_dict.update(additional_vars)
            
        vars_dict['user_id'] = context.user_id
        vars_dict['tenant_id'] = context.tenant_id
        
        tpl = Template(template.system_instruction)
        return tpl.safe_substitute(**vars_dict)
