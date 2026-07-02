from collections.abc import AsyncIterator

from google.genai import types

from app.infrastructure.ai.models import StreamChunk


class GeminiStreamAdapter:
    """Adapter for mapping Gemini stream responses to StreamChunk sequence."""

    @staticmethod
    async def process_stream(
        response_stream: AsyncIterator[types.GenerateContentResponse],
        provider_name: str,
        model: str,
        start_time: float,
    ) -> AsyncIterator[StreamChunk]:
        chunk_index = 0
        prev_chunk = None

        async for chunk in response_stream:
            if prev_chunk is not None:
                yield StreamChunk(
                    content=prev_chunk.text or "",
                    is_final=False,
                )
            prev_chunk = chunk

        if prev_chunk is not None:
            # This is the last chunk
            prompt_tokens = (
                getattr(prev_chunk.usage_metadata, "prompt_token_count", None)
                if hasattr(prev_chunk, "usage_metadata")
                else None
            )
            completion_tokens = (
                getattr(prev_chunk.usage_metadata, "candidates_token_count", None)
                if hasattr(prev_chunk, "usage_metadata")
                else None
            )

            yield StreamChunk(
                content=prev_chunk.text or "",
                is_final=True,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
