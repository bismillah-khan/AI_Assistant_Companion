from threading import Lock

import asyncio

from sentence_transformers import SentenceTransformer

from app.core.config.settings import Settings

_MODEL = None
_MODEL_LOCK = Lock()


def _get_model(settings: Settings) -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                _MODEL = SentenceTransformer(settings.embedding_model)
    return _MODEL


class EmbeddingClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        def _encode() -> list[list[float]]:
            model = _get_model(self.settings)
            embeddings = model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()

        return await asyncio.to_thread(_encode)

    async def embed_query(self, text: str) -> list[float]:
        return (await self.embed_texts([text]))[0]
