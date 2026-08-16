"""
Prints the Microsoft OAuth authorization URL.
Copy the URL and paste it into your browser to authenticate.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.connectors.oauth.providers.microsoft import MicrosoftOAuthProvider

provider = MicrosoftOAuthProvider()
client_id = os.getenv("MICROSOFT_OAUTH_CLIENT_ID")
redirect_uri = os.getenv("MICROSOFT_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")

url = provider.build_auth_url(
    client_id=client_id,
    redirect_uri=redirect_uri,
    state="default_tenant|microsoft"
)

print("\n" + "=" * 70)
print("STEP 1: Copy the URL below and paste it into your browser:")
print("=" * 70)
print(url)
print("=" * 70)
print("\nSTEP 2: Sign in with your Microsoft account and click Accept.")
print("STEP 3: After seeing 'Authentication Successful', run:")
print("   python scripts/connect_comm_services.py (choose 3)")
print("   OR run the test directly -- the callback server must be running.\n")
