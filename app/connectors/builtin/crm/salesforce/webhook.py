import structlog

logger = structlog.get_logger(__name__)

async def handle_salesforce_webhook(payload: dict) -> dict:
    """Handle incoming Salesforce push notification."""
    logger.info("Received Salesforce push notification", payload=payload)
    return {"status": "ACKNOWLEDGED"}
