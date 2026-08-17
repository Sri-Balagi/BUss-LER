import structlog
from app.connectors.sdk.registry.capability_registry import ConnectorCapabilityRegistry

# Import built-in connectors using their actual class names
from app.connectors.builtin.email.outlook.connector import OutlookConnector
from app.connectors.builtin.email.gmail.connector import GmailConnector
from app.connectors.builtin.productivity.onenote.connector import OneNoteConnector
from app.connectors.builtin.productivity.todo.connector import TodoConnector
from app.connectors.builtin.storage.onedrive.connector import OneDriveConnector
from app.connectors.builtin.storage.gdrive.connector import GoogleDriveConnector
from app.connectors.builtin.calendar.gcalendar.connector import GoogleCalendarConnector
from app.connectors.builtin.crm.hubspot.connector import HubSpotConnector
from app.connectors.builtin.crm.salesforce.connector import SalesforceConnector

logger = structlog.get_logger(__name__)

def bootstrap_connectors():
    """Register all built-in connectors into the CapabilityRegistry."""
    logger.info("Bootstrapping connectors")

    # Instantiate and register each connector
    connectors = [
        OutlookConnector(),
        GmailConnector(),
        OneNoteConnector(),
        TodoConnector(),
        OneDriveConnector(),
        GoogleDriveConnector(),
        GoogleCalendarConnector(),
        HubSpotConnector(),
        SalesforceConnector(),
    ]

    for connector in connectors:
        ConnectorCapabilityRegistry.register_connector(connector)

    logger.info(f"Successfully registered {len(connectors)} connectors.")
