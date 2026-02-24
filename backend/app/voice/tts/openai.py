import asyncio
import logging
from typing import AsyncIterator

import httpx

from app.core.config.settings import Settings
from app.core.errors import AppError
from app.voice.tts.base import AUDIO_MIME_TYPES, TTSResult

logger = logging.getLogger(__name__)


class OpenAITTSClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def synthesize(self, text: str, voice: str, fmt: str) -> TTSResult:
        payload = self._payload(text, voice, fmt)
        data = await self._post_bytes("/v1/audio/speech", payload)
        media_type = AUDIO_MIME_TYPES.get(fmt, "application/octet-stream")
        return TTSResult(audio_bytes=data, media_type=media_type, file_ext=fmt)

    async def stream(self, text: str, voice: str, fmt: str) -> AsyncIterator[bytes]:
        payload = self._payload(text, voice, fmt)
        url = f"{self.settings.tts_api_base.rstrip('/')}/v1/audio/speech"
        headers = self._headers()

        async with httpx.AsyncClient(timeout=self.settings.tts_timeout_seconds) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk

    def _payload(self, text: str, voice: str, fmt: str) -> dict[str, object]:
        if not text:
            raise AppError("missing_text", status_code=400)
        return {
            "model": self.settings.tts_model,
            "voice": voice,
            "input": text,
            "response_format": fmt,
        }

    def _headers(self) -> dict[str, str]:
        api_key = self.settings.tts_api_key or self.settings.llm_api_key
        if not api_key:
            raise AppError("tts_api_key_missing", status_code=500)
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _post_bytes(self, path: str, payload: dict[str, object]) -> bytes:
        url = f"{self.settings.tts_api_base.rstrip('/')}{path}"
        headers = self._headers()

        for attempt in range(1, self.settings.llm_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.tts_timeout_seconds) as client:
                    response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.content
            except httpx.HTTPError as exc:
                if attempt >= self.settings.llm_max_retries:
                    logger.exception("tts_request_failed")
                    raise AppError("tts_request_failed", status_code=502) from exc
                backoff = 0.5 * (2 ** (attempt - 1))
                await asyncio.sleep(backoff)
        raise AppError("tts_request_failed", status_code=502)
