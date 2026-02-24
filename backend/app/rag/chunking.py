from typing import Iterable


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> Iterable[str]:
    if chunk_size <= 0:
        return []

    step = max(1, chunk_size - max(0, chunk_overlap))
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks
