"""BizOS Platform Status Inspector — bizos status"""

import httpx
import sys


def run(args=None):
    url = getattr(args, "url", "http://localhost:8000/api/v1/system/liveness") if args else "http://localhost:8000/api/v1/system/liveness"

    print("\n========================================================================")
    print("  [BizOS Platform Runtime Status]")
    print("========================================================================")

    try:
        response = httpx.get(url, timeout=3.0)
        if response.status_code == 200:
            print("  [OK] BizOS API Gateway   : RUNNING (HTTP 200)")
            print(f"  Detail                   : {response.json()}")
        else:
            print(f"  [WARN] BizOS API Gateway : UNHEALTHY (HTTP {response.status_code})")
    except Exception:
        print("  [OFFLINE] BizOS API Gateway is not currently running.")
        print("  Tip                      : Run 'bizos start' to launch the platform.")

    print("========================================================================\n")
