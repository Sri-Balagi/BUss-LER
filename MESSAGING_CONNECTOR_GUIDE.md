# Enterprise Communication Connector Suite & Developer Guide

## 1. Suite Overview

The **BizOS Communication Suite** expands the Connector Ecosystem to support real-world messaging platforms (WhatsApp, Slack, MS Teams, Telegram, Discord, Facebook Messenger, Instagram, Twilio, Outlook, etc.) built on top of `BaseMessagingConnector`.

```
                  ┌──────────────────────┐
                  │ BaseMessagingConnector│
                  └──────────┬───────────┘
                             │
 ┌───────────────────────────┼───────────────────────────┐
 ▼                           ▼                           ▼
[WhatsAppConnector]  [SlackConnector]           [TeamsConnector]
 (OAuth2 + Webhooks) (OAuth2 + Threads)        (Graph API + Webhooks)
```

---

## 2. Modular Messaging SDK Components

- **`BaseMessagingConnector` (`app/connectors/sdk/messaging/base.py`)**: Abstract base extending `BaseConnector` with `send_message()`, `reply_message()`, `list_conversations()`, and `get_presence()`.
- **Template Framework (`templates.py`)**: `CanonicalTemplate` and `TemplateRenderer` for structured template messages.
- **Media Framework (`media.py`)**: `MediaUploader` and `MediaDownloader` helpers for handling file attachments.
- **Presence & Typing (`presence.py`)**: `PresenceManager` and `TypingHandler` for real-time presence indicators.

---

## 3. Canonical Domain Extensions (`app/connectors/canonical/messaging.py`)

All messaging data is normalized into canonical business models before leaving the connector boundary:
- `CanonicalAttachment`
- `CanonicalReaction`
- `CanonicalContact`
- `CanonicalGroup`
- `CanonicalPresence`
- `CanonicalDeliveryReceipt`
- `CanonicalTypingEvent`

---

## 4. Capability Matrix Quick Reference

See the full [Capability Matrix](file:///C:/Users/Sri%20Balagi/.gemini/antigravity-ide/brain/13a6893f-cb4a-49c9-9258-f677800b0a8a/capability_matrix.md) for a feature-by-feature comparison across all connectors.
