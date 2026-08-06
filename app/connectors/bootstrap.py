import structlog
from app.connectors.sdk.registry.capability_registry import ConnectorCapabilityRegistry

# Import built-in connectors
from app.connectors.builtin.email.outlook.connector import MicrosoftOutlookConnector
from app.connectors.builtin.email.gmail.connector import GmailConnector
from app.connectors.builtin.productivity.onenote.connector import MicrosoftOneNoteConnector
from app.connectors.builtin.productivity.todo.connector import MicrosoftTodoConnector
from app.connectors.builtin.storage.onedrive.connector import MicrosoftOneDriveConnector
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
        MicrosoftOutlookConnector(),
        GmailConnector(),
        MicrosoftOneNoteConnector(),
        MicrosoftTodoConnector(),
        MicrosoftOneDriveConnector(),
        GoogleDriveConnector(),
        GoogleCalendarConnector(),
        HubSpotConnector(),
        SalesforceConnector(),
    ]
    
    for connector in connectors:
        ConnectorCapabilityRegistry.register_connector(connector)
        
    logger.info(f"Successfully registered {len(connectors)} connectors.")
