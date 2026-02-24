import tempfile
from pathlib import Path

from fastapi import UploadFile

from app.core.config.settings import get_settings
from app.core.errors import AppError
from app.voice.stt.whisper import WhisperClient


class VoiceService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.whisper = WhisperClient(self.settings)

    async def transcribe(self, file: UploadFile) -> str:
        if not file.filename:
            raise AppError("missing_filename", status_code=400)

        suffix = Path(file.filename).suffix or ".wav"
        temp_path = Path(tempfile.mkstemp(suffix=suffix)[1])

        try:
            data = await file.read()
            if not data:
                raise AppError("empty_audio", status_code=400)

            temp_path.write_bytes(data)
            return await self.whisper.transcribe_file(temp_path)
        except AppError:
            raise
        except Exception as exc:
            raise AppError("transcription_failed", status_code=500) from exc
        finally:
            await file.close()
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass
