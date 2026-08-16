"""AI dependencies for API v1."""

from app.bootstrap.container import get_container
from app.infrastructure.ai.kernel import AbstractAIKernel


async def get_ai_kernel() -> AbstractAIKernel:
    """Resolve the AI Kernel from the DI container."""
    return get_container().resolve(AbstractAIKernel)
