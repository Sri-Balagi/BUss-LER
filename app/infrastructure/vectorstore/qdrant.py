"""Qdrant Client wrapper and Vector Infrastructure Manager.

Provides a singleton connection to Qdrant vector database,
robust health checks, and idempotent collection initialization.
This infrastructure layer is completely domain-agnostic and prepares
the database for generic vector implementations (Memories, Goals, Agents).
"""

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.config import Settings

logger = structlog.get_logger()


class QdrantService:
    """Connection manager for the Qdrant vector database."""

    _instance: AsyncQdrantClient | None = None

    @classmethod
    def get_client(cls, settings: Settings) -> AsyncQdrantClient:
        """Get or initialize the Qdrant client singleton."""
        if cls._instance is None:
            if settings.is_test:
                cls._instance = AsyncQdrantClient(location=":memory:")
            else:
                cls._instance = AsyncQdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port,
                    timeout=10,
                )
        return cls._instance

    @classmethod
    async def initialize_collections(cls, settings: Settings) -> None:
        """Ensure required collections exist with correct parameters.

        This method is idempotent and should be called on startup.
        """
        client = cls.get_client(settings)
        collection_name = settings.qdrant_collection

        try:
            exists = await client.collection_exists(collection_name=collection_name)
            if not exists:
                logger.info(
                    "Initializing Qdrant collection",
                    collection=collection_name,
                    vector_size=settings.qdrant_vector_size,
                    distance=settings.qdrant_distance_metric,
                )

                distance_metric = models.Distance.COSINE
                if settings.qdrant_distance_metric.upper() == "EUCLID":
                    distance_metric = models.Distance.EUCLID
                elif settings.qdrant_distance_metric.upper() == "DOT":
                    distance_metric = models.Distance.DOT

                await client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=settings.qdrant_vector_size,
                        distance=distance_metric,
                        on_disk=False,  # Keep in memory for speed in MVP
                    ),
                    optimizers_config=models.OptimizersConfigDiff(indexing_threshold=100),
                )

                # Apply initialization metadata (collection versioning)
                # We can store this in Qdrant using collection properties or just log it.
                logger.info(
                    "Qdrant collection created",
                    collection=collection_name,
                    version="v1",
                )

                # Create standard payload indices for hybrid filtering
                indices = [
                    ("twin_id", models.PayloadSchemaType.KEYWORD),
                    ("memory_category", models.PayloadSchemaType.KEYWORD),
                    ("source", models.PayloadSchemaType.KEYWORD),
                ]

                for field_name, schema_type in indices:
                    await client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field_name,
                        field_schema=schema_type,
                    )
            else:
                logger.info("Qdrant collection already exists", collection=collection_name)

        except Exception as e:
            logger.error("Failed to initialize Qdrant collections", error=str(e))
            raise

    @classmethod
    async def health_check(cls, settings: Settings) -> dict:
        """Validate Qdrant connectivity and collection state.

        Returns:
            dict with health status details.
        """
        client = cls.get_client(settings)
        collection_name = settings.qdrant_collection
        status = {"status": "unhealthy", "qdrant": False, "collection": False}

        try:
            # 1. Test connectivity
            collections = await client.get_collections()
            status["qdrant"] = True

            # 2. Test collection configuration
            collection_names = [c.name for c in collections.collections]
            if collection_name in collection_names:
                info = await client.get_collection(collection_name)
                vectors = info.config.params.vectors if info and info.config and info.config.params else None
                config_size = vectors.size if isinstance(vectors, models.VectorParams) else settings.qdrant_vector_size

                if config_size == settings.qdrant_vector_size:
                    status["collection"] = True
                    status["vector_size"] = config_size
                    status["status"] = "healthy"
                else:
                    status["detail"] = (
                        f"Vector size mismatch. Expected {settings.qdrant_vector_size}, got {config_size}"
                    )
            else:
                status["detail"] = f"Collection '{collection_name}' not found."

        except Exception as e:
            logger.error("Qdrant health check failed", error=str(e))
            status["detail"] = str(e)

        return status

    @classmethod
    async def close(cls) -> None:
        """Close the client connection."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
