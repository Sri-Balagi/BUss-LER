from .slack import SlackOAuthProvider
from .microsoft import MicrosoftOAuthProvider
from .google import GoogleOAuthProvider
from .hubspot import HubSpotOAuthProvider
from .salesforce import SalesforceOAuthProvider

__all__ = [
    "SlackOAuthProvider",
    "MicrosoftOAuthProvider",
    "GoogleOAuthProvider",
    "HubSpotOAuthProvider",
    "SalesforceOAuthProvider",
]
