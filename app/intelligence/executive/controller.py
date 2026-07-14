"""ExecutiveController — the lifecycle orchestrator for Autonomous Intelligence.

Replaces the Wave-0 ExecutiveIntelligenceOrchestrator. Manages session setup,
pub/sub bridging, state machine transitions, and delegates the actual loop
execution to the CognitivePipeline.
"""

from typing import Any
from uuid import UUID

import structlog

from app.intelligence.core.session.events import (
    SessionEvent,
    SessionEventBus,
    SessionEventType,
)
from app.intelligence.core.session.models import ReasoningMode, SessionLifecycleState
from app.intelligence.executive.interfaces import IExecutiveController
from app.intelligence.executive.session_factory import SessionFactory
from app.intelligence.integration.interfaces import ICognitivePipeline
from app.intelligence.integration.models import ExecutiveIntelligenceResult

logger = structlog.get_logger(__name__)


class ExecutiveController(IExecutiveController):
    """Production orchestrator for Wave-1 cognitive loops."""

    def __init__(self, pipeline: ICognitivePipeline, session_factory: SessionFactory):
        self.pipeline = pipeline
        self.session_factory = session_factory
        # In a full distributed environment, active_sessions would be backed by Redis.
        # For M7, it is an in-memory dictionary.
        self._active_sessions: dict[str, Any] = {}

    async def process_request(
        self,
        raw_request: str,
        twin_id: UUID | None = None,
        mode: ReasoningMode = ReasoningMode.ANALYTICAL,
    ) -> ExecutiveIntelligenceResult:
        """Entry point for a new autonomous execution session."""
        
        logger.info(
            "Starting new autonomous session",
            twin_id=str(twin_id) if twin_id else "none",
            mode=mode.value,
        )

        # 1. Create the rich domain aggregate (M7 upgrade)
        session = await self.session_factory.create_session(
            twin_id=twin_id, raw_request=raw_request, mode=mode
        )

        # 2. Setup session-scoped EventBus (M7 upgrade)
        event_bus = SessionEventBus(session.session_id)
        await event_bus.start()

        # Track session internally
        self._active_sessions[session.session_id] = {
            "session": session,
            "event_bus": event_bus,
        }

        # 3. Transition to RUNNING
        session.transition(SessionLifecycleState.RUNNING)
        event_bus.publish(
            SessionEvent(
                session_id=session.session_id,
                event_type=SessionEventType.CYCLE_STARTED,
                payload={"mode": mode.value},
            )
        )

        try:
            # 4. Delegate to the Cognitive Pipeline
            # Note: The Wave-0 pipeline signature is preserved for backward compatibility
            # during M7. In M8, this will become an async continuous loop.
            result = self.pipeline.run_pipeline(raw_request, session)
            
            # M7: Transition to completed since run_pipeline is currently synchronous
            if session.lifecycle_state == SessionLifecycleState.RUNNING:
                session.transition(SessionLifecycleState.COMPLETED)
                
            event_bus.publish(
                SessionEvent(
                    session_id=session.session_id,
                    event_type=SessionEventType.SESSION_COMPLETED,
                )
            )
            return result

        except Exception as e:
            logger.error(
                "Cognitive session failed",
                session_id=session.session_id,
                error=str(e),
                exc_info=True,
            )
            if not session.is_terminal:
                session.transition(SessionLifecycleState.FAILED, reason=str(e))
                event_bus.publish(
                    SessionEvent(
                        session_id=session.session_id,
                        event_type=SessionEventType.SESSION_FAILED,
                        payload={"error": str(e)},
                    )
                )
            raise
        
        finally:
            # Cleanup resources
            await event_bus.stop()
            self._active_sessions.pop(session.session_id, None)

    async def resume_session(
        self, session_id: str, trigger_event: Any = None
    ) -> ExecutiveIntelligenceResult:
        """Resume a suspended session.
        
        For M7, this is a stub as the M7 pipeline is synchronous.
        Will be fully implemented in M10 (Autonomous Resumption).
        """
        logger.warning(
            "resume_session called but M7 pipeline is synchronous",
            session_id=session_id,
        )
        raise NotImplementedError("Session resumption requires the M8 async pipeline.")
