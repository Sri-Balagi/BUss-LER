from abc import ABC, abstractmethod

from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult


class IMiddleware(ABC):
    """
    Canonical interface for Capability Middleware.
    """

    @abstractmethod
    async def before_execution(
        self,
        request: CapabilityRequest,
        cap_context: CapabilityContext,
        mw_context: MiddlewareContext
    ) -> MiddlewareDecision:
        """
        Invoked before the capability executes.
        Can inspect, enrich the contexts, or reject the request.
        """
        pass

    @abstractmethod
    async def after_execution(
        self,
        request: CapabilityRequest,
        cap_context: CapabilityContext,
        mw_context: MiddlewareContext,
        result: CapabilityResult
    ) -> CapabilityResult:
        """
        Invoked after the capability executes.
        Can observe, enrich, or mutate the CapabilityResult.
        """
        pass

    @abstractmethod
    async def on_exception(
        self,
        request: CapabilityRequest,
        cap_context: CapabilityContext,
        mw_context: MiddlewareContext,
        exception: Exception
    ) -> MiddlewareDecision:
        """
        Invoked if an exception bubbles up.
        Can observe the failure or dictate a RETRY.
        """
        pass
