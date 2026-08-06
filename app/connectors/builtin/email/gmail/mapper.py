from typing import Any, Dict, List
import base64
from app.connectors.sdk.canonical import CanonicalEmail

def map_gmail_to_canonical(gmail_data: Dict[str, Any]) -> CanonicalEmail:
    """Map a raw Gmail API message to a CanonicalEmail object."""
    headers = gmail_data.get("payload", {}).get("headers", [])
    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
    to = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
    
    recipients = [r.strip() for r in to.split(",")] if to else []
    
    return CanonicalEmail(
        email_id=gmail_data.get("id", ""),
        thread_id=gmail_data.get("threadId"),
        sender=sender,
        recipients=recipients,
        subject=subject,
        body_text=gmail_data.get("snippet", ""),
        snippet=gmail_data.get("snippet", ""),
        labels=gmail_data.get("labelIds", []),
        raw_provider_id="google"
    )
