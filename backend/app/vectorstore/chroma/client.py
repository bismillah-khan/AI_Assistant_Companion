from typing import Any

import chromadb

from app.core.config.settings import Settings


class ChromaStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = chromadb.PersistentClient(path=settings.vector_store_path)
        self._collection = self._client.get_or_create_collection("rag")

    async def add_texts(self, texts: list[str], embeddings: list[list[float]], metadata: list[dict]) -> None:
        ids = [f"doc-{index}" for index in range(len(texts))]
        self._collection.add(documents=texts, embeddings=embeddings, metadatas=metadata, ids=ids)

    async def similarity_search(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        results = self._collection.query(query_embeddings=[embedding], n_results=top_k)
        hits: list[dict[str, Any]] = []
        for doc, meta, dist in zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0],
            strict=False,
        ):
            hits.append({"text": doc, "metadata": meta, "score": float(dist)})
        return hits
