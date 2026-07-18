import uuid
from typing import AsyncIterator, List

from app.domain.applications.base import IStreamingCognitiveApplication, ApplicationResponse
from app.domain.applications.context.models import ApplicationContext, ChatContext
from app.domain.applications.registry.models import ApplicationMetadata
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.platform import IIntelligencePlatform, UnifiedExecutionRequest

class CopilotApplication(IStreamingCognitiveApplication):
    """Conversational Copilot application using IIntelligencePlatform."""
    
    def __init__(self, platform: IIntelligencePlatform):
        self._platform = platform

    def metadata(self) -> ApplicationMetadata:
        return ApplicationMetadata(
            id="bizos.copilot.v1",
            name="BizOS Conversational Copilot",
            description="General purpose AI copilot for BizOS.",
            version="1.0.0",
            supported_capabilities=[
                CapabilityType.REASONING,
                CapabilityType.RETRIEVAL,
                CapabilityType.PLANNING
            ]
        )

    def supported_capabilities(self) -> List[CapabilityType]:
        return self.metadata().supported_capabilities

    async def execute(self, context: ApplicationContext) -> ApplicationResponse:
        """Fallback synchronous execution."""
        if not isinstance(context, ChatContext):
            raise ValueError("CopilotApplication requires a ChatContext")
            
        try:
            tenant_uuid = uuid.UUID(context.tenant_id)
        except ValueError:
            tenant_uuid = None
            
        request = UnifiedExecutionRequest(
            request_type="reasoning",
            tenant_id=tenant_uuid,
            input_data={"message": context.variables.get("message", "")},
            correlation_id=context.trace_id or str(uuid.uuid4())
        )
        
        result = await self._platform.execute_request(request)
        return ApplicationResponse(data=result.output_data, metadata={"metrics": result.metrics.model_dump()})

    async def execute_stream(self, context: ApplicationContext) -> AsyncIterator[ApplicationResponse]:
        """Streaming execution."""
        response = await self.execute(context)
        yield response

    def health(self) -> bool:
        return True
