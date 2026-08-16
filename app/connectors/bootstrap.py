import structlog
from app.connectors.sdk.registry.capability_registry import ConnectorCapabilityRegistry

logger = structlog.get_logger(__name__)

def bootstrap_connectors():
    """Register all built-in connectors into the CapabilityRegistry."""
    logger.info("Bootstrapping connectors")
    
    connectors = []
    
    # 1. Outlook
    try:
        from app.connectors.builtin.email.outlook.connector import OutlookConnector
        connectors.append(OutlookConnector())
    except Exception as e:
        logger.warning(f"OutlookConnector skipped: {e}")

    # 2. Gmail
    try:
        from app.connectors.builtin.email.gmail.connector import GmailConnector
        connectors.append(GmailConnector())
    except Exception as e:
        logger.warning(f"GmailConnector skipped: {e}")

    # 3. OneNote
    try:
        from app.connectors.builtin.productivity.onenote.connector import OneNoteConnector
        connectors.append(OneNoteConnector())
    except Exception as e:
        logger.warning(f"OneNoteConnector skipped: {e}")

    # 4. Todo
    try:
        from app.connectors.builtin.productivity.todo.connector import TodoConnector
        connectors.append(TodoConnector())
    except Exception as e:
        logger.warning(f"TodoConnector skipped: {e}")

    # 5. OneDrive
    try:
        from app.connectors.builtin.storage.onedrive.connector import OneDriveConnector
        connectors.append(OneDriveConnector())
    except Exception as e:
        logger.warning(f"OneDriveConnector skipped: {e}")

    # 6. Google Drive
    try:
        from app.connectors.builtin.storage.gdrive.connector import GoogleDriveConnector
        connectors.append(GoogleDriveConnector())
    except Exception as e:
        logger.warning(f"GoogleDriveConnector skipped: {e}")

    # 7. Google Calendar
    try:
        from app.connectors.builtin.calendar.gcalendar.connector import GoogleCalendarConnector
        connectors.append(GoogleCalendarConnector())
    except Exception as e:
        logger.warning(f"GoogleCalendarConnector skipped: {e}")

    # 8. HubSpot
    try:
        from app.connectors.builtin.crm.hubspot.connector import HubSpotConnector
        connectors.append(HubSpotConnector())
    except Exception as e:
        logger.warning(f"HubSpotConnector skipped: {e}")

    # 9. Salesforce
    try:
        from app.connectors.builtin.crm.salesforce.connector import SalesforceConnector
        connectors.append(SalesforceConnector())
    except Exception as e:
        logger.warning(f"SalesforceConnector skipped: {e}")
    
    for connector in connectors:
        try:
            ConnectorCapabilityRegistry.register_connector(connector)
        except Exception as e:
            logger.warning(f"Failed to register connector {connector}: {e}")
        
    logger.info(f"Successfully registered {len(connectors)} connectors.")
