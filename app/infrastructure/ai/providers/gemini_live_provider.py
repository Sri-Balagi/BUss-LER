"""Live Gemini 2.5 Flash Provider for BizOS domain intelligence layer using google-genai SDK."""

import asyncio
import json
import os
import time
from typing import Any, List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types

from app.config import get_settings
from app.domain.intelligence.llm_provider import ILLMProvider


class GeminiLiveProvider(ILLMProvider):
    """Real Gemini 2.5 Flash LLM provider leveraging the official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self._model = model or settings.gemini_flash_model or "gemini-2.5-flash"
        self._client = genai.Client(api_key=self._api_key)
        self.last_latency_ms: float = 0.0
        self.last_prompt_tokens: int = 0
        self.last_completion_tokens: int = 0

    @property
    def provider_name(self) -> str:
        return "gemini-flash"

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None,
    ) -> BaseModel:
        target_model = model or self._model
        t0 = time.perf_counter()

        # Build schema instructions into prompt or config
        prompt_with_instructions = (
            f"{prompt}\n\n"
            f"Output MUST be valid JSON adhering strictly to this JSON Schema:\n"
            f"{json.dumps(schema.model_json_schema())}"
        )

        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        )

        try:
            res = await self._client.aio.models.generate_content(
                model=target_model,
                contents=prompt_with_instructions,
                config=config,
            )
            self.last_latency_ms = (time.perf_counter() - t0) * 1000

            if hasattr(res, "usage_metadata") and res.usage_metadata:
                self.last_prompt_tokens = getattr(res.usage_metadata, "prompt_token_count", 0) or 0
                self.last_completion_tokens = getattr(res.usage_metadata, "candidates_token_count", 0) or 0

            text = res.text or "{}"
            # Clean markdown code blocks if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("```", 1)[0]
            
            return schema.model_validate_json(text.strip())

        except Exception as e:
            # Fallback parsing or re-raise
            raise RuntimeError(f"Gemini live structured generation failed: {e}") from e

    async def chat_completion(
        self,
        messages: List[dict[str, str]],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None,
    ) -> str:
        target_model = model or self._model
        t0 = time.perf_counter()

        prompt_lines = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            prompt_lines.append(f"{role}: {content}")
        prompt_str = "\n".join(prompt_lines)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                res = await self._client.aio.models.generate_content(
                    model=target_model,
                    contents=prompt_str,
                    config=types.GenerateContentConfig(temperature=0.7),
                )
                self.last_latency_ms = (time.perf_counter() - t0) * 1000

                if hasattr(res, "usage_metadata") and res.usage_metadata:
                    self.last_prompt_tokens = getattr(res.usage_metadata, "prompt_token_count", 0) or 0
                    self.last_completion_tokens = getattr(res.usage_metadata, "candidates_token_count", 0) or 0

                return res.text or ""
            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2.0 * (attempt + 1))
                        continue
                raise RuntimeError(f"Gemini chat completion failed: {e}") from e

    async def generate_embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        target_model = model or "gemini-embedding-001"
        try:
            res = await self._client.aio.models.embed_content(
                model=target_model,
                contents=text,
            )
            if res and res.embeddings and len(res.embeddings) > 0:
                vals = list(res.embeddings[0].values)
                return vals[:768] if len(vals) >= 768 else vals
            return [0.0] * 768
        except Exception as e:
            raise RuntimeError(f"Gemini embedding failed: {e}") from e
