import io
from typing import Iterable

from pypdf import PdfReader

from app.core.errors import AppError


def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:
        raise AppError("invalid_pdf", status_code=400) from exc

    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts).strip()


def iter_texts(text: str) -> Iterable[str]:
    if text:
        yield text
