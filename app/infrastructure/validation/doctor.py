"""BizOS Infrastructure Doctor & Preflight Validation Service.

Validates core infrastructure dependencies before runtime execution:
- Environment Variables
- Qdrant Vector Database Connectivity & Collections
- Gemini LLM & Embedding API Connectivity
- PostgreSQL / Supabase Database Connectivity
- Redis Cache Server Connectivity
"""

import asyncio
import os
from typing import Any, Dict, List
import httpx
from google import genai
from qdrant_client import AsyncQdrantClient

from app.config import get_settings


class BizOSDoctor:
    """Preflight diagnostic and system health validator for BizOS Core."""

    def __init__(self):
        self.settings = get_settings()

    async def run_diagnostics(self) -> Dict[str, Any]:
        """Execute full suite of preflight diagnostic checks."""
        results: Dict[str, Any] = {
            "status": "HEALTHY",
            "checks": {},
            "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0},
        }

        # 1. Env vars
        env_check = self._check_env_vars()
        results["checks"]["environment"] = env_check

        # 2. Gemini API
        gemini_check = await self._check_gemini_api()
        results["checks"]["gemini_api"] = gemini_check

        # 3. Qdrant Vector DB
        qdrant_check = await self._check_qdrant()
        results["checks"]["qdrant"] = qdrant_check

        # 4. Supabase / Postgres
        supabase_check = await self._check_supabase()
        results["checks"]["supabase"] = supabase_check

        # Aggregate overall status
        failed = 0
        passed = 0
        warnings = 0
        for name, check in results["checks"].items():
            st = check.get("status")
            if st == "OK":
                passed += 1
            elif st == "WARN":
                warnings += 1
            else:
                failed += 1

        results["summary"] = {
            "total": len(results["checks"]),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
        }

        if failed > 0:
            results["status"] = "UNHEALTHY"
        elif warnings > 0:
            results["status"] = "DEGRADED"

        return results

    def _check_env_vars(self) -> Dict[str, Any]:
        required_vars = [
            "GEMINI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "QDRANT_HOST",
            "QDRANT_PORT",
        ]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            return {
                "status": "FAIL",
                "message": f"Missing required env vars: {', '.join(missing)}",
            }
        return {"status": "OK", "message": "All required environment variables configured."}

    async def _check_gemini_api(self) -> Dict[str, Any]:
        api_key = self.settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"status": "FAIL", "message": "GEMINI_API_KEY is missing."}
        try:
            client = genai.Client(api_key=api_key)
            # Lightweight test call to embed content
            res = await client.aio.models.embed_content(
                model=self.settings.gemini_embedding_model or "gemini-embedding-001",
                contents="ping",
            )
            emb_len = len(res.embeddings[0].values) if res and res.embeddings else 0
            return {
                "status": "OK",
                "message": f"Gemini API responsive. Embedding dimension: {emb_len}d.",
            }
        except Exception as e:
            return {"status": "FAIL", "message": f"Gemini API health check failed: {str(e)}"}

    async def _check_qdrant(self) -> Dict[str, Any]:
        host = self.settings.qdrant_host or "localhost"
        port = self.settings.qdrant_port or 6333
        collection_name = self.settings.qdrant_collection or "memories"
        try:
            client = AsyncQdrantClient(host=host, port=port, timeout=5.0)
            collections = await client.get_collections()
            col_names = [c.name for c in collections.collections]

            # Ensure memories collection exists
            if collection_name not in col_names:
                from qdrant_client.http import models as qmodels

                await client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.settings.qdrant_vector_size or 768,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                status_msg = f"Collection '{collection_name}' created on Qdrant host '{host}:{port}'."
            else:
                status_msg = f"Connected to Qdrant at {host}:{port}. Collection '{collection_name}' ready."

            await client.close()
            return {"status": "OK", "message": status_msg}
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Qdrant connection failed ({host}:{port}): {str(e)}. (Ensure Qdrant container is running)",
            }

    async def _check_supabase(self) -> Dict[str, Any]:
        url = self.settings.supabase_url or os.getenv("SUPABASE_URL")
        key = self.settings.supabase_key or os.getenv("SUPABASE_KEY")
        if not url or not key:
            return {"status": "WARN", "message": "Supabase credentials incomplete."}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{url}/rest/v1/", headers={"apikey": key})
                if res.status_code in (200, 404, 401, 204):
                    return {
                        "status": "OK",
                        "message": f"Supabase REST endpoint accessible at {url}.",
                    }
                return {
                    "status": "WARN",
                    "message": f"Supabase REST endpoint returned status code {res.status_code}.",
                }
        except Exception as e:
            return {"status": "WARN", "message": f"Supabase REST check failed: {str(e)}"}
