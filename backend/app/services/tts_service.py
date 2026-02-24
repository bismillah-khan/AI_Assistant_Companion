from typing import AsyncIterator

from app.core.config.settings import get_settings
from app.core.errors import AppError
from app.models.voice import TTSRequest
from app.voice.tts.base import AUDIO_MIME_TYPES, TTSResult
from app.voice.tts.local import LocalTTSClient
from app.voice.tts.openai import OpenAITTSClient


class TTSService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.local = LocalTTSClient()
        self.openai = OpenAITTSClient(self.settings)

    async def synthesize(self, request: TTSRequest) -> TTSResult:
        provider = self.settings.tts_provider
        voice = request.voice or self.settings.tts_voice
        fmt = request.format or self.settings.tts_format

        if provider == "openai":
            return await self.openai.synthesize(request.text, voice, fmt)
        if provider == "local":
            return await self.local.synthesize(request.text, voice, fmt)

        raise AppError("tts_provider_not_supported", status_code=500)

    async def stream(self, request: TTSRequest) -> tuple[AsyncIterator[bytes], str] | None:
        if not request.stream:
            return None

        provider = self.settings.tts_provider
        voice = request.voice or self.settings.tts_voice
        fmt = request.format or self.settings.tts_format

        if provider == "openai":
            media_type = AUDIO_MIME_TYPES.get(fmt, "application/octet-stream")
            return self.openai.stream(request.text, voice, fmt), media_type

        return None
