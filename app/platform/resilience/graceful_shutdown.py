"""Graceful shutdown handler for BizOS.

Registers SIGTERM and SIGINT handlers to allow the application to
finish in-flight requests before exiting.
"""

from __future__ import annotations

import asyncio
import signal

import structlog

logger = structlog.get_logger()

_shutdown_event: asyncio.Event | None = None


def get_shutdown_event() -> asyncio.Event:
    """Return the global shutdown event, creating it if necessary."""
    global _shutdown_event  # noqa: PLW0603
    if _shutdown_event is None:
        _shutdown_event = asyncio.Event()
    return _shutdown_event


def register_shutdown_handlers() -> None:
    """Register SIGTERM and SIGINT handlers for graceful shutdown."""
    try:
        loop = asyncio.get_event_loop()
        event = get_shutdown_event()

        def _handle_signal(sig: signal.Signals) -> None:
            logger.info("Shutdown signal received", signal=sig.name)
            event.set()

        loop.add_signal_handler(signal.SIGTERM, _handle_signal, signal.SIGTERM)
        loop.add_signal_handler(signal.SIGINT, _handle_signal, signal.SIGINT)
        logger.info("Graceful shutdown handlers registered")
    except (NotImplementedError, RuntimeError):
        # Windows does not support add_signal_handler on the event loop.
        # Signal handling will rely on the default Python handlers.
        logger.info("Graceful shutdown via asyncio signal handlers not available on this platform")
