import asyncio
import os
import sys
import uvicorn
from multiprocessing import Process
from dotenv import load_dotenv

# Add project root to python path so it can find the 'app' module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We need to import the router from our app
from app.connectors.webhooks.oauth_callback import router, oauth_manager
from fastapi import FastAPI, Request

# Ensure .env is loaded
load_dotenv()

app = FastAPI(title="BizOS Local OAuth Server")
app.include_router(router)

@app.get("/callback")
async def forward_callback(request: Request):
    from fastapi.responses import RedirectResponse
    query = request.scope.get("query_string", b"").decode("utf-8")
    return RedirectResponse(f"/connectors/oauth/callback?{query}")

def run_server():
    print("[Starting local callback server on http://localhost:8080/callback]")
    uvicorn.run(app, host="localhost", port=8080, log_level="warning")

async def main():
    print("========================================")
    print("  BizOS Connector Auth Setup")
    print("========================================")
    print("Which service to connect?")
    print("  1) Gmail (Google Workspace)")
    print("  2) Slack")
    print("  3) Outlook (Microsoft 365)")
    print("  4) MS Teams (Microsoft 365)")
    print("  5) All")
    
    choice = input("\nChoice: ")
    
    providers = []
    if choice in ("2", "5"):
        providers.append("slack")
    
    if choice in ("3", "4", "5"):
        providers.append("microsoft")
    
    if not providers:
        print("Skipping or unimplemented choice.")
        return

    # Start local server in background
    server_process = Process(target=run_server)
    server_process.start()

    import webbrowser
    import time
    
    try:
        # Give server a second to start
        time.sleep(2)
        
        for provider_id in providers:
            print(f"\n[Setting up {provider_id}]")
            client_id = os.getenv(f"{provider_id.upper()}_OAUTH_CLIENT_ID")
            redirect_uri = os.getenv(f"{provider_id.upper()}_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
            
            if not client_id:
                print(f"Error: Missing {provider_id.upper()}_OAUTH_CLIENT_ID in .env")
                continue
                
            auth_url = oauth_manager.get_auth_url(
                provider_id=provider_id,
                client_id=client_id,
                redirect_uri=redirect_uri,
                state=f"default_tenant|{provider_id}"
            )
            
            print(f"[Opening browser -> {provider_id.capitalize()} OAuth consent screen...]")
            webbrowser.open(auth_url)
            
            print("Waiting for authorization code (check browser)...")
            # In a real CLI script we'd wait for a signal from the callback endpoint
            # For simplicity, we just prompt the user once they're done
            input("Press Enter once the browser says 'Authentication Successful'...")
            
            print(f"\u2713 {provider_id.capitalize()} connector is ready")
            
    finally:
        print("Shutting down local server...")
        server_process.terminate()
        server_process.join()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
