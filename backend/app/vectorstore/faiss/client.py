import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.config.settings import Settings


class FaissStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._dir = Path(settings.vector_store_path)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._dir / "index.faiss"
        self._meta_path = self._dir / "metadata.json"
        self._index = None
        self._metadata: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self._index_path.exists():
            self._index = faiss.read_index(str(self._index_path))
        if self._meta_path.exists():
            self._metadata = json.loads(self._meta_path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        if self._index is not None:
            faiss.write_index(self._index, str(self._index_path))
        self._meta_path.write_text(json.dumps(self._metadata), encoding="utf-8")

    async def add_texts(self, texts: list[str], embeddings: list[list[float]], metadata: list[dict]) -> None:
        vectors = np.array(embeddings, dtype="float32")
        if self._index is None:
            self._index = faiss.IndexFlatIP(vectors.shape[1])
        self._index.add(vectors)
        for text, meta in zip(texts, metadata, strict=False):
            self._metadata.append({"text": text, "metadata": meta})
        self._save()

    async def similarity_search(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        if self._index is None or not self._metadata:
            return []
        vector = np.array([embedding], dtype="float32")
        scores, indices = self._index.search(vector, top_k)
        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0 or idx >= len(self._metadata):
                continue
            payload = dict(self._metadata[idx])
            payload["score"] = float(score)
            results.append(payload)
        return results
