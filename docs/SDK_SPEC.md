# BizOS Client SDK Specification (Wave 7)

## Overview
The BizOS Client SDK abstracts all transport layers (REST, SSE, and future WebSockets) to provide a clean, domain-driven interface for frontend applications and human-in-the-loop (HitL) integration.

## Interfaces (TypeScript Example)

```typescript
import { BizOSClient } from '@bizos/client-sdk';

const client = new BizOSClient({
    baseUrl: 'https://api.bizos.io',
    apiKey: 'your_api_key'
});

// ==========================================
// 1. Session Management
// ==========================================

// Creates a new session (HTTP POST /api/v1/sessions)
const session = await client.sessions.create({
    tenant_id: 'tenant-123',
    user_id: 'user-456'
});

// ==========================================
// 2. Event Streaming (Abstracts SSE)
// ==========================================

// Subscribe to events filtered by session ID.
// Internally uses SSE (`GET /api/v1/events/stream?session_id=...`).
// If WebSockets replace SSE in the future, this interface will remain exactly the same.
const subscription = client.events.subscribe({
    session_id: session.session_id
}, (event) => {
    console.log("Received event:", event.type, event.data);
    
    if (event.type === 'ApprovalRequestedEvent') {
        handleApprovalRequest(event.data.approval_id);
    }
});

// Clean up
subscription.unsubscribe();

// ==========================================
// 3. Approval Domain
// ==========================================

async function handleApprovalRequest(approvalId: string) {
    // Fetch details (HTTP GET /api/v1/approvals/:id)
    const approval = await client.approvals.get(approvalId);
    
    // Approve (HTTP POST /api/v1/approvals/:id/approve)
    await client.approvals.approve(approvalId, {
        user_id: 'user-456'
    });
    
    // Or Reject (HTTP POST /api/v1/approvals/:id/reject)
    // await client.approvals.reject(approvalId, {
    //     user_id: 'user-456',
    //     reason: 'Not aligned with policy.'
    // });
}
```

## Interfaces (Python Example)

```python
from bizos.client import BizOSClient

client = BizOSClient(base_url="https://api.bizos.io", api_key="your_api_key")

# 1. Sessions
session = client.sessions.create(tenant_id="tenant-123", user_id="user-456")

# 2. Events (Async)
async def on_event(event):
    if event.type == "ApprovalRequestedEvent":
        await client.approvals.approve(
            approval_id=event.data.approval_id, 
            user_id="user-456"
        )

# Subscribe (internally manages SSE stream)
client.events.subscribe(session_id=session.session_id, callback=on_event)
```

## Architectural Guarantee
The SDK will never expose `SSE` or `REST` specific terminology. It will always expose the domain capabilities: `client.events`, `client.approvals`, and `client.sessions`.
