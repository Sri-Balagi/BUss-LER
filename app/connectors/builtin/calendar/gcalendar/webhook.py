import structlog

logger = structlog.get_logger(__name__)

async def handle_gcal_webhook(payload: dict) -> dict:
    """Handle incoming Google Calendar push notification."""
    logger.info("Received Google Calendar push notification", payload=payload)
    return {"status": "ACKNOWLEDGED"}
