"""Generic Multi-Format Knowledge Ingestion Pipeline.

Supports chunking and vector indexing of:
- Markdown (.md)
- Structured JSON (.json)
- CSV Datasets (.csv)
- Plain Text (.txt)
"""

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.domain.memory.models import MemoryRecord, MemoryType, MemorySource
from app.domain.memory.provider import IMemoryProvider


class DocumentChunk:
    def __init__(self, content: str, source: str, title: str, metadata: Optional[Dict[str, Any]] = None):
        self.chunk_id = str(uuid4())
        self.content = content
        self.source = source
        self.title = title
        self.metadata = metadata or {}


class KnowledgeIngestionPipeline:
    """Ingests multi-format business documents into the vector memory provider."""

    def __init__(self, memory_provider: IMemoryProvider, chunk_size: int = 500, chunk_overlap: int = 50):
        self._memory_provider = memory_provider
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def ingest_markdown(self, title: str, content: str, source: str = "markdown_file") -> List[str]:
        chunks = self._split_text(content, title, source)
        ingested_ids = []
        for c in chunks:
            rec = MemoryRecord(
                title=f"[{title}] Chunk {c.chunk_id[:8]}",
                content=c.content,
                memory_type=MemoryType.KNOWLEDGE,
                source=MemorySource.SYSTEM,
            )
            await self._memory_provider.store(rec)
            ingested_ids.append(str(rec.memory_id))
        return ingested_ids

    async def ingest_json(self, title: str, data: Any, source: str = "json_file") -> List[str]:
        if isinstance(data, list):
            items = data
        else:
            items = [data]

        ingested_ids = []
        for i, item in enumerate(items):
            item_str = json.dumps(item, indent=2)
            rec = MemoryRecord(
                title=f"[{title}] Item #{i+1}",
                content=item_str,
                memory_type=MemoryType.KNOWLEDGE,
                source=MemorySource.SYSTEM,
            )
            await self._memory_provider.store(rec)
            ingested_ids.append(str(rec.memory_id))
        return ingested_ids

    async def ingest_batch_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        total_chunks = 0
        doc_count = 0
        for doc in documents:
            title = doc.get("title", "Untitled Document")
            content = doc.get("content", "")
            source = doc.get("source", "batch_ingestion")
            doc_type = doc.get("type", "markdown")

            if doc_type == "json":
                ids = await self.ingest_json(title, doc.get("data", {}), source)
            else:
                ids = await self.ingest_markdown(title, content, source)

            total_chunks += len(ids)
            doc_count += 1

        return {"documents_processed": doc_count, "total_chunks_indexed": total_chunks}

    def _split_text(self, text: str, title: str, source: str) -> List[DocumentChunk]:
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_length = 0

        for p in paragraphs:
            p_len = len(p)
            if current_length + p_len > self._chunk_size and current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(DocumentChunk(content=chunk_text, source=source, title=title))
                current_chunk = []
                current_length = 0
            current_chunk.append(p)
            current_length += p_len

        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(DocumentChunk(content=chunk_text, source=source, title=title))

        return chunks
