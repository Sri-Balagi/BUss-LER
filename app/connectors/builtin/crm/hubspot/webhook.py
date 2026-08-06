import structlog

logger = structlog.get_logger(__name__)

async def handle_hubspot_webhook(payload: dict) -> dict:
    """Handle incoming HubSpot push notification."""
    logger.info("Received HubSpot push notification", payload=payload)
    return {"status": "ACKNOWLEDGED"}
