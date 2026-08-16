import time

from app.runtime.capabilities.adapters.base import IResourceAdapter
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.interfaces import ICapability
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult, ExecutionStatus
from app.runtime.capabilities.models.specification import CapabilitySpecification


class BaseCapability(ICapability):
    """
    Abstract base capability.
    Manages adapter delegation and response transformation.
    """

    def __init__(self, spec: CapabilitySpecification, adapter: IResourceAdapter):
        self.spec = spec
        self.adapter = adapter
        self.context: CapabilityContext | None = None

    async def initialize(self, context: CapabilityContext) -> None:
        self.context = context
        await self.adapter.initialize()
        await self.adapter.connect()

    async def validate(self, request: CapabilityRequest) -> None:
        # Basic validation that request matches capability
        if request.capability_id != self.spec.capability_id:
            raise ValueError(
                f"Request capability_id {request.capability_id} does not match spec {self.spec.capability_id}"
            )
        if request.operation not in self.spec.supported_operations:
            raise ValueError(
                f"Operation {request.operation} not supported by capability {self.spec.capability_id}"
            )

    async def execute(self, request: CapabilityRequest) -> CapabilityResult:
        start_time = time.time()
        try:
            # Delegate entirely to the adapter for physical execution
            raw_result = await self.adapter.execute(request)

            execution_time_ms = int((time.time() - start_time) * 1000)
            return CapabilityResult(
                status=ExecutionStatus.SUCCESS,
                outputs=raw_result,
                execution_time_ms=execution_time_ms,
                execution_trace_id=request.trace_id,
            )
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return CapabilityResult(
                status=ExecutionStatus.FAILURE,
                outputs={},
                errors=[str(e)],
                execution_time_ms=execution_time_ms,
                execution_trace_id=request.trace_id,
            )

    async def cleanup(self) -> None:
        await self.adapter.disconnect()
        await self.adapter.cleanup()
