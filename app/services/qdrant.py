"""Qdrant client wrapper.

Provides a singleton connection to Qdrant vector database and
initialization helpers for collections used by BizOS.
"""

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.config import Settings

logger = structlog.get_logger()


class QdrantService:
    """Wrapper for the Qdrant async Python client."""

    _instance: AsyncQdrantClient | None = None

    @classmethod
    def get_client(cls, settings: Settings) -> AsyncQdrantClient:
        """Get or initialize the Qdrant client singleton."""
        if cls._instance is None:
            cls._instance = AsyncQdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        return cls._instance

    @classmethod
    async def initialize_collections(cls, settings: Settings) -> None:
        """Ensure required collections exist with correct parameters."""
        client = cls.get_client(settings)
        
        # Collection for MVP Memory Engine
        # Defined here for M0 startup testing, will be used in M2
        collection_name = "bizos_memories"
        
        try:
            exists = await client.collection_exists(collection_name=collection_name)
            if not exists:
                logger.info("Creating Qdrant collection", collection=collection_name)
                await client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=768,  # text-embedding-004 output size
                        distance=models.Distance.COSINE,
                        on_disk=False,  # Keep in memory for MVP speed
                    ),
                    optimizers_config=models.OptimizersConfigDiff(
                        indexing_threshold=100
                    )
                )
                
                # Create payload indexes for fast filtering
                await client.create_payload_index(
                    collection_name=collection_name,
                    field_name="entity_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                await client.create_payload_index(
                    collection_name=collection_name,
                    field_name="memory_type",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                await client.create_payload_index(
                    collection_name=collection_name,
                    field_name="domain_tags",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
            else:
                logger.info("Qdrant collection already exists", collection=collection_name)
                
        except Exception as e:
            logger.error("Failed to initialize Qdrant collections", error=str(e))
            raise

    @classmethod
    async def close(cls) -> None:
        """Close the client connection."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
