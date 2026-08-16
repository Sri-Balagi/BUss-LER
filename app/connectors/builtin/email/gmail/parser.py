def parse_gmail_message(raw_payload: str) -> str:
    """Parse a base64 encoded Gmail message."""
    import base64
    try:
        return base64.urlsafe_b64decode(raw_payload).decode("utf-8")
    except Exception:
        return raw_payload
