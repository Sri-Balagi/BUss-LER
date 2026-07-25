# BizOS Connector SDK & Developer Guide

## 1. Connector Platform Architecture

The BizOS Connector Platform enables hot-pluggable, enterprise-grade integrations across hundreds of services (GitHub, Gmail, Slack, Stripe, Jira, etc.).

```
BizOS Core / Agents / Workflows
            │
    [Capability Registry / Tool Layer]
            │
    [Connector Manager & Lifecycle]
            │
 ┌──────────┴──────────┐
 │  BaseConnector SDK  │
 └──────────┬──────────┘
            ├─ OAuthConnector
            ├─ APIKeyConnector
            ├─ WebhookConnector
            └─ PollingConnector
```

---

## 2. Key Framework Components

| Component | Directory | Description |
|---|---|---|
| **Connector SDK** | `app/connectors/sdk/` | Abstract base classes (`BaseConnector`, `OAuthConnector`, etc.) and Mixins. |
| **Manifest System** | `app/connectors/registry/manifest.py` | Declarative descriptor for connector identity, scopes, capabilities, AI metadata, marketplace info. |
| **Registry & Loader** | `app/connectors/registry/` | Automatic filesystem discovery of connector packages via `importlib`. |
| **Connector Manager** | `app/connectors/manager/` | Multi-profile lifecycle runtime manager (`INSTALLED -> CONFIGURED -> CONNECTED -> ACTIVE`). |
| **Capability Framework** | `app/connectors/capabilities/` | Enables BizOS to reason about *what a connector can do* rather than vendor-specific details. |
| **Secret Vault** | `app/connectors/secrets/` | Secure storage and masking for OAuth tokens, API keys, and certificates. |
| **State Store** | `app/connectors/state/` | Persistent storage for cursors, checkpoints, etags, and page tokens. |
| **Rate Limiter & Retry** | `app/connectors/ratelimit/`, `retry/` | Token Bucket / Sliding Window rate limiting and exponential backoff retry. |
| **Generic Scheduler** | `app/connectors/scheduler/` | Task scheduler for sync, token refresh, health checks, and renewals. |
| **Canonical Models** | `app/connectors/canonical/` | Vendor-agnostic data representation layer (User, Issue, Message, Payment, etc.). |
| **Transformation Pipeline** | `app/connectors/transforms/`, `mapping/` | Normalization pipeline transforming raw vendor payloads to canonical objects. |
| **Audit Logger** | `app/connectors/audit/` | Audit event logging published on the `connector.audit.*` SystemBus namespace. |
| **AI Tool Layer** | `app/connectors/tools/` | Exposes connector capabilities as agent-callable tools (`ConnectorTool`). |
| **Inbound Webhook Router** | `app/connectors/webhooks/` | Centralized FastAPI router at `/api/v1/webhooks/{connector_id}`. |

---

## 3. How to Build a New Connector in 4 Steps

### Step 1: Create Package Directory
Create a subfolder under `app/connectors/builtin/<connector_id>/` containing `manifest.py` and `connector.py`.

### Step 2: Define `manifest.py`
Expose a top-level `MANIFEST` object:

```python
from app.connectors.registry.manifest import ConnectorManifest, CapabilityDeclaration, AuthType, SyncType

MANIFEST = ConnectorManifest(
    id="custom_service",
    name="Custom Service Connector",
    version="1.0.0",
    auth_type=AuthType.API_KEY,
    capabilities=[
        CapabilityDeclaration(
            capability_id="custom.data_sync",
            name="Data Sync",
            operations=["list_items"],
            canonical_model="CanonicalTask",
        )
    ],
    supported_sync_types=[SyncType.INCREMENTAL],
)
```

### Step 3: Implement `connector.py`
Inherit from the appropriate SDK base class:

```python
from app.connectors.sdk.api_key import APIKeyConnector

class CustomConnector(APIKeyConnector):
    def get_capabilities(self) -> list[str]:
        return ["custom.data_sync"]

    async def _ping(self) -> bool:
        return True

    async def _fetch_page(self, cursor: str | None = None):
        return [{"id": "1", "name": "Item 1"}], None

    async def _process_record(self, record: dict):
        pass
```

### Step 4: Register Factory & Auto-Discovery
`ConnectorLoader` automatically discovers any folder under `app/connectors/builtin/` with a valid `manifest.py`.
Register its class factory with `ConnectorManager.register_factory("custom_service", CustomConnector)`.
