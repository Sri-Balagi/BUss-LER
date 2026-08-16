import time
from typing import Any

import structlog

from app.intelligence.core.session.events import (
    SessionEvent,
    SessionEventType,
)
from app.intelligence.core.session.models import CycleRecord, SessionLifecycleState
from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.pipeline.interfaces import IAsyncCognitivePipeline
from app.intelligence.pipeline.phases import IPhase, PhaseResultStatus

logger = structlog.get_logger(__name__)


class AsyncCognitivePipeline(IAsyncCognitivePipeline):
    """The production async OS loop for Wave-1.

    Iterates through the registered phases until the session reaches a terminal
    state or yields for human approval.
    """

    def __init__(self, phases: list[IPhase], event_bus_factory: Any = None) -> None:
        # Expected to be ordered: Observe -> Understand -> Reason -> Plan -> Delegate -> Execute -> Reflect -> Learn
        self.phases = phases
        self.event_bus_factory = event_bus_factory

    async def run_loop(self, session: CognitiveSession) -> None:
        logger.info("Starting async pipeline loop", session_id=session.session_id)

        # M8: Stub event bus access for telemetry if factory is provided, otherwise skip.
        # In full wiring, the ExecutiveController manages the bus.
        event_bus = self.event_bus_factory(session.session_id) if self.event_bus_factory else None

        while session.is_runnable and not session.should_terminate():
            cycle_start = time.time()
            phase_results: dict[str, str] = {}
            cycle_success = True

            for phase in self.phases:
                if not session.is_runnable:
                    break # Stop if a previous phase suspended or terminated the session

                phase_start = time.time()
                try:
                    result = await phase.execute(session)
                    phase_results[phase.phase_type.value] = result.status.value

                    # Emit structured telemetry
                    if event_bus:
                        event_bus.publish(
                            SessionEvent(
                                session_id=session.session_id,
                                event_type=SessionEventType.PHASE_COMPLETED,
                                payload={
                                    "phase": phase.phase_type.value,
                                    "status": result.status.value,
                                    "duration_ms": (time.time() - phase_start) * 1000
                                }
                            )
                        )

                    if result.status == PhaseResultStatus.YIELDED:
                        # Phase hit a suspension condition (e.g., waiting for human approval)
                        logger.info("Pipeline yielded", phase=phase.phase_type.value)
                        session.transition(SessionLifecycleState.AWAITING_INPUT, reason=f"Yielded by {phase.phase_type}")
                        break

                    if result.status == PhaseResultStatus.FAILED:
                        logger.error("Phase failed", phase=phase.phase_type.value, error=result.error_message)
                        cycle_success = False
                        break # Abort the rest of the cycle

                except Exception as e:
                    logger.error("Phase execution exception", phase=phase.phase_type.value, error=str(e), exc_info=True)
                    phase_results[phase.phase_type.value] = PhaseResultStatus.FAILED.value
                    cycle_success = False

                    if event_bus:
                        event_bus.publish(
                            SessionEvent(
                                session_id=session.session_id,
                                event_type=SessionEventType.PHASE_FAILED,
                                payload={"phase": phase.phase_type.value, "error": str(e)}
                            )
                        )
                    break

            # Record cycle completion
            duration_ms = (time.time() - cycle_start) * 1000

            record = CycleRecord(
                cycle_index=len(session.execution_history),
                duration_ms=duration_ms,
                phase_results=phase_results,
                succeeded=cycle_success,
                failure_reason="Phase aborted" if not cycle_success else None
            )
            session.record_cycle(record)

            # Check termination
            if session.should_terminate() and session.lifecycle_state not in [SessionLifecycleState.AWAITING_INPUT, SessionLifecycleState.FAILED]:
                session.transition(SessionLifecycleState.COMPLETED, reason="Loop criteria met")

        logger.info("Exited async pipeline loop", session_state=session.lifecycle_state.value)
