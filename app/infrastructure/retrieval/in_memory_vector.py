import asyncio
from typing import List, Dict
from uuid import UUID

from app.domain.retrieval.models import RetrievalContext, RetrievalResultItem, RetrievalSource
from app.domain.retrieval.vector_store import IVectorRepository


class InMemoryVectorRepository(IVectorRepository):
    """
    A naive in-memory vector repository for storage-agnostic testing.
    In a real implementation, this would connect to Qdrant or Pinecone.
    """
    
    def __init__(self):
        self._documents: Dict[UUID, dict] = {}
        self._lock = asyncio.Lock()

    async def add_document(self, entity_id: UUID, content: str, vector: List[float], metadata: dict = None):
        """Helper to seed mock data during tests."""
        async with self._lock:
            self._documents[entity_id] = {
                "content": content,
                "vector": vector,
                "metadata": metadata or {}
            }

    async def search(self, context: RetrievalContext) -> List[RetrievalResultItem]:
        query_text = context.query.query_text.lower()
        results = []
        
        async with self._lock:
            for entity_id, doc in self._documents.items():
                # Filter by tenant if provided
                if context.tenant_id and doc["metadata"].get("tenant_id") != context.tenant_id:
                    continue
                    
                # Very naive text-based similarity since this is a mock
                # (Real implementation would use cosine similarity on `context.query.query_vector`)
                doc_content = doc["content"].lower()
                
                if query_text in doc_content:
                    # Dummy relevance score based on length ratio or exact match
                    relevance = 0.8
                    
                    item = RetrievalResultItem(
                        source=RetrievalSource.VECTOR,
                        entity_id=entity_id,
                        content=doc["content"],
                        relevance_score=relevance,
                        confidence=0.9,
                        provenance_chain=["InMemoryVectorStore"],
                        metadata=doc["metadata"]
                    )
                    results.append(item)
                    
        # Sort and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[context.offset : context.offset + context.limit]
