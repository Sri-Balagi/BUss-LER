import asyncio
import json
from app.connectors.oauth.token_repository import OAuthTokenRepository
from app.connectors.builtin.email.outlook.connector import OutlookConnector
from app.domain.shared.context import ExecutionContext, PrincipalType

async def main():
    ctx = ExecutionContext(
        tenant_id="default_tenant",
        principal_type=PrincipalType.HUMAN,
        principal_id="test_principal",
        session_id="test",
        conversation_id="test",
        trace_id="test",
        correlation_id="test"
    )
    
    print("Checking Sent Items folder in Outlook...")
    connector = OutlookConnector()
    try:
        res = await connector.execute_action("read_sent", {"limit": 3}, ctx)
        emails = res.get("emails", [])
        
        if not emails:
            print("No sent emails found recently.")
        else:
            print(f"Found {len(emails)} recently sent emails:")
            for e in emails:
                print("-" * 50)
                print(f"To:      {e.get('recipients')}")
                print(f"Subject: {e.get('subject')}")
                print(f"Time:    {e.get('date_received')}")
                print(f"Body:    {e.get('body_text', '')[:100]}...")
    except Exception as e:
        print(f"Error fetching sent emails: {e}")

if __name__ == "__main__":
    asyncio.run(main())
