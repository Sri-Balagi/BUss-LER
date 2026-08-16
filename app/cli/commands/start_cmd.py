"""BizOS Service Launcher — bizos start"""

import os
import sys
import subprocess


def run(args=None):
    host = getattr(args, "host", "0.0.0.0") if args else "0.0.0.0"
    port = getattr(args, "port", 8000) if args else 8000
    reload_flag = getattr(args, "reload", False) if args else False

    print("\n========================================================================")
    print("  [BizOS AI Operating System — Service Launcher]")
    print("========================================================================")
    print(f"  Starting BizOS API Server on http://{host}:{port}")
    print("  Docs available at: http://localhost:8000/docs")
    print("------------------------------------------------------------------------\n")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    if reload_flag:
        cmd.append("--reload")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n  [OK] BizOS server stopped cleanly.")
    except Exception as exc:
        print(f"\n  [ERROR] Server launch failed: {exc}")
