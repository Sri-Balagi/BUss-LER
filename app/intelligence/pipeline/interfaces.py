from abc import ABC, abstractmethod

from app.intelligence.core.session.session import CognitiveSession


class IAsyncCognitivePipeline(ABC):
    """The continuous asynchronous cognitive loop."""

    @abstractmethod
    async def run_loop(self, session: CognitiveSession) -> None:
        """Run the cognitive loop continuously until convergence, failure, or suspension.

        Mutates the session state and appends CycleRecords directly.
        """
        pass
