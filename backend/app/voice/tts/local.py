import asyncio
import logging
import tempfile
from pathlib import Path
from threading import Lock

import pyttsx3

from app.core.errors import AppError
from app.voice.tts.base import AUDIO_MIME_TYPES, TTSResult

logger = logging.getLogger(__name__)

_ENGINE = None
_ENGINE_LOCK = Lock()


def _get_engine() -> pyttsx3.Engine:
    global _ENGINE
    if _ENGINE is None:
        with _ENGINE_LOCK:
            if _ENGINE is None:
                _ENGINE = pyttsx3.init()
    return _ENGINE


def _select_voice(engine: pyttsx3.Engine, voice: str | None) -> None:
    if not voice:
        return
    for item in engine.getProperty("voices"):
        if voice.lower() in item.name.lower() or voice.lower() in item.id.lower():
            engine.setProperty("voice", item.id)
            return


class LocalTTSClient:
    async def synthesize(self, text: str, voice: str, fmt: str) -> TTSResult:
        if fmt != "wav":
            raise AppError("local_tts_format_not_supported", status_code=400)
        if not text:
            raise AppError("missing_text", status_code=400)

        temp_path = Path(tempfile.mkstemp(suffix=".wav")[1])

        def _render() -> bytes:
            engine = _get_engine()
            _select_voice(engine, voice)
            engine.save_to_file(text, str(temp_path))
            engine.runAndWait()
            return temp_path.read_bytes()

        try:
            audio_bytes = await asyncio.to_thread(_render)
            return TTSResult(
                audio_bytes=audio_bytes,
                media_type=AUDIO_MIME_TYPES["wav"],
                file_ext="wav",
            )
        except Exception as exc:
            logger.exception("local_tts_failed")
            raise AppError("local_tts_failed", status_code=500) from exc
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass
