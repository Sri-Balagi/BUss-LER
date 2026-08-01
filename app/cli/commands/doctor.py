"""BizOS Diagnostic Inspector — bizos doctor"""

import asyncio
import os
import sys
import time
import httpx
from typing import Dict, Any

from app.config import Settings
from app.infrastructure.vectorstore.qdrant import QdrantService
from app.infrastructure.ai.providers.gemini.provider import GeminiProvider


class DiagnosticInspector:
    def __init__(self, settings: Settings | None = None):
        try:
            self.settings = settings or Settings()
        except Exception:
            self.settings = None

    async def check_python_environment(self) -> Dict[str, Any]:
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        valid = sys.version_info >= (3, 10)
        return {
            "name": "Python Environment",
            "status": "OK" if valid else "FAIL",
            "detail": f"Python {version} (>= 3.10 required)"
        }

    async def check_settings(self) -> Dict[str, Any]:
        if not self.settings:
            return {
                "name": "Environment Configuration (.env)",
                "status": "FAIL",
                "detail": "Failed to load .env settings. Missing required variables (GEMINI_API_KEY, SUPABASE_URL, etc.)"
            }
        return {
            "name": "Environment Configuration (.env)",
            "status": "OK",
            "detail": f"Loaded configuration for environment '{self.settings.app_env}'"
        }

    async def check_qdrant(self) -> Dict[str, Any]:
        if not self.settings:
            return {"name": "Qdrant Vector DB", "status": "SKIP", "detail": "Settings not loaded"}
        try:
            health = await QdrantService.health_check(self.settings)
            status = health.get("status", "unhealthy").upper()
            if status == "HEALTHY":
                return {
                    "name": "Qdrant Vector DB",
                    "status": "OK",
                    "detail": f"Connected to {self.settings.qdrant_host}:{self.settings.qdrant_port} (Collection: {self.settings.qdrant_collection})"
                }
            else:
                return {
                    "name": "Qdrant Vector DB",
                    "status": "WARN",
                    "detail": f"Qdrant reachable but reported status: {health.get('detail', 'vector size check')}"
                }
        except Exception as exc:
            return {
                "name": "Qdrant Vector DB",
                "status": "FAIL",
                "detail": f"Could not connect to Qdrant at {self.settings.qdrant_host}:{self.settings.qdrant_port} ({str(exc)})"
            }

    async def check_gemini(self) -> Dict[str, Any]:
        if not self.settings or not self.settings.gemini_api_key:
            return {"name": "Gemini AI Provider", "status": "FAIL", "detail": "GEMINI_API_KEY is not set"}
        try:
            provider = GeminiProvider(self.settings)
            res = await provider.health_check()
            return {
                "name": "Gemini AI Provider",
                "status": "OK",
                "detail": f"Gemini API key validated (Model: {self.settings.gemini_flash_model})"
            }
        except Exception as exc:
            return {
                "name": "Gemini AI Provider",
                "status": "FAIL",
                "detail": f"Gemini health check failed: {str(exc)}"
            }

    async def check_storage_permissions(self) -> Dict[str, Any]:
        try:
            test_file = ".bizos_doctor_write_test"
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            return {
                "name": "Storage & Permissions",
                "status": "OK",
                "detail": "Workspace directory is writable"
            }
        except Exception as exc:
            return {
                "name": "Storage & Permissions",
                "status": "FAIL",
                "detail": f"Directory permission check failed: {str(exc)}"
            }

    async def check_supabase(self) -> Dict[str, Any]:
        if not self.settings or not self.settings.supabase_url:
            return {"name": "Supabase Connection", "status": "SKIP", "detail": "SUPABASE_URL not configured"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.settings.supabase_url}/rest/v1/")
                if res.status_code in (200, 401, 404):
                    return {
                        "name": "Supabase Connection",
                        "status": "OK",
                        "detail": f"Reachable at {self.settings.supabase_url}"
                    }
                return {
                    "name": "Supabase Connection",
                    "status": "WARN",
                    "detail": f"Responded with status code {res.status_code}"
                }
        except Exception as exc:
            return {
                "name": "Supabase Connection",
                "status": "WARN",
                "detail": f"Could not ping Supabase endpoint ({str(exc)})"
            }

    async def run_diagnostics(self) -> bool:
        print("\n========================================================================")
        print("  [BizOS Platform Diagnostics & Health Inspector]")
        print("========================================================================\n")

        checks = [
            self.check_python_environment(),
            self.check_settings(),
            self.check_storage_permissions(),
            self.check_gemini(),
            self.check_qdrant(),
            self.check_supabase(),
        ]

        results = await asyncio.gather(*checks)
        all_passed = True

        for res in results:
            status = res["status"]
            if status == "OK":
                icon = "[  OK  ]"
            elif status == "WARN":
                icon = "[ WARN ]"
            elif status == "SKIP":
                icon = "[ SKIP ]"
            else:
                icon = "[ FAIL ]"
                all_passed = False

            print(f"  {icon} {res['name']:<30} : {res['detail']}")

        print("\n------------------------------------------------------------------------")
        if all_passed:
            print("  [OK] Platform status: PRODUCTION READY (All required checks passed)")
        else:
            print("  [!]  Platform status: ISSUES DETECTED (Please review warnings/failures above)")
        print("========================================================================\n")
        return all_passed


def run(args=None):
    inspector = DiagnosticInspector()
    success = asyncio.run(inspector.run_diagnostics())
    if not success and args and getattr(args, "strict", False):
        sys.exit(1)
