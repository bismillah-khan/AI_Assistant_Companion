from typing import Iterable

from app.core.config.settings import Settings, get_settings
from app.core.errors import AppError
from app.rag.chunking import chunk_text
from app.rag.embeddings import EmbeddingClient
from app.rag.ingest import extract_pdf_text
from app.vectorstore.chroma.client import ChromaStore
from app.vectorstore.faiss.client import FaissStore


class RAGService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.embeddings = EmbeddingClient(self.settings)
        self.store = self._init_store()

    def _init_store(self):
        if self.settings.vector_db == "chroma":
            return ChromaStore(self.settings)
        return FaissStore(self.settings)

    async def ingest_pdf_bytes(self, pdf_bytes: bytes, source: str) -> int:
        text = extract_pdf_text(pdf_bytes)
        if not text:
            raise AppError("empty_pdf", status_code=400)

        chunks = list(chunk_text(text, self.settings.chunk_size, self.settings.chunk_overlap))
        if not chunks:
            raise AppError("empty_chunks", status_code=400)

        embeddings = await self.embeddings.embed_texts(chunks)
        metadata = [{"source": source, "chunk": index} for index in range(len(chunks))]
        await self.store.add_texts(chunks, embeddings, metadata)
        return len(chunks)

    async def retrieve_context(self, query: str) -> str:
        if not query:
            return ""
        embedding = await self.embeddings.embed_query(query)
        hits = await self.store.similarity_search(embedding, self.settings.rag_top_k)
        return "\n\n".join(hit["text"] for hit in hits)
