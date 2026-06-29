"""Provider Timeout & Retry Strategy — Extension F.

Wraps each AbstractContextProvider invocation with configurable timeout
and exponential backoff retry. No single provider can block assembly indefinitely.
"""

import asyncio
import random
from typing import Optional, Union, Tuple, Type
from uuid import UUID

from pydantic import ConfigDict
import structlog

from app.intelligence.intake.situation.enterprise_context import ContextSection, ProviderFailureRecord
from app.shared.enums import ContextSource
from app.interfaces.http.schemas.base import DomainBaseModel

logger = structlog.get_logger(__name__)


class ProviderRetryConfig(DomainBaseModel):
    """Timeout and retry configuration for a single context provider.

    Attributes:
        timeout_seconds: Maximum time allowed per attempt.
        max_retries:     Number of retries after the initial attempt.
        backoff_base:    Base for exponential backoff (base * 2^attempt).
        max_delay:       Maximum backoff delay allowed.
        jitter:          Whether to apply jitter to the delay.
        retry_on:        Exception classes that trigger a retry.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    timeout_seconds: float = 5.0
    max_retries: int = 2
    backoff_base: float = 1.0
    max_delay: float = 10.0
    jitter: bool = True
    retry_on: Tuple[Type[Exception], ...] = (Exception,)


async def provide_with_retry(
    provider,
    retry_config: ProviderRetryConfig,
    ctx,
    twin_id: UUID,
    policy,
    source: ContextSource,
    context_id: Optional[UUID] = None,
    event_bus=None,
) -> Union[ContextSection, ProviderFailureRecord]:
    """Execute a provider with timeout and exponential backoff retry.

    On success: returns ContextSection.
    On exhausted retries: returns ProviderFailureRecord (never raises).

    Args:
        provider:      AbstractContextProvider instance.
        retry_config:  Timeout and retry parameters.
        ctx:           OperationContext for the current request.
        twin_id:       Target Digital Twin.
        policy:        Active ContextPolicy.
        source:        ContextSource identifier for this provider.
        context_id:    Optional ID of the context being assembled (for events).
        event_bus:     Optional EventBus for ContextProviderFailedEvent.
    """
    last_error: str = "unknown"
    attempt = 0

    while attempt <= retry_config.max_retries:
        try:
            result = await asyncio.wait_for(
                provider.provide(ctx, twin_id, policy),
                timeout=retry_config.timeout_seconds,
            )
            if attempt > 0:
                logger.info(
                    "Provider recovered after retry",
                    source=source.value,
                    attempt=attempt,
                )
            return result

        except asyncio.TimeoutError:
            last_error = f"TimeoutError after {retry_config.timeout_seconds}s"
            logger.warning(
                "Provider timed out",
                source=source.value,
                attempt=attempt,
                timeout_seconds=retry_config.timeout_seconds,
            )

        except Exception as exc:
            if not isinstance(exc, retry_config.retry_on):
                exc_name = type(exc).__name__
                last_error = f"{exc_name}: {exc}"
                logger.warning(
                    "Provider raised non-retryable error",
                    source=source.value,
                    error=last_error,
                    attempt=attempt,
                )
                break

            exc_name = type(exc).__name__
            last_error = f"{exc_name}: {exc}"
            logger.warning(
                "Provider raised retryable error",
                source=source.value,
                error=last_error,
                attempt=attempt,
            )

        attempt += 1
        if attempt <= retry_config.max_retries:
            # Exponential backoff: base * 2^(attempt-1) since attempt is 1 for the first retry
            delay = retry_config.backoff_base * (2 ** (attempt - 1))
            if retry_config.jitter:
                delay = delay * random.uniform(0.5, 1.5)

            delay = min(delay, retry_config.max_delay)
            await asyncio.sleep(delay)

    # All retries exhausted — publish event and return ProviderFailureRecord
    total_attempts = attempt
    logger.error(
        "Provider exhausted all retries",
        source=source.value,
        attempts=total_attempts,
        last_error=last_error,
    )

    if event_bus is not None:
        try:
            from app.shared.events.models import ContextProviderFailedEvent

            event = ContextProviderFailedEvent(
                correlation_id=ctx.correlation_id,
                context_id=context_id,
                twin_id=twin_id,
                provider=source.value,
                attempts=total_attempts,
                last_error=last_error,
            )
            event_bus.publish(event)
        except Exception as evt_exc:
            logger.warning(
                "Failed to publish ContextProviderFailedEvent", error=str(evt_exc)
            )

    return ProviderFailureRecord(
        provider=source,
        error_type=last_error.split(":")[0],
        error_message=last_error,
        attempts=total_attempts,
    )
