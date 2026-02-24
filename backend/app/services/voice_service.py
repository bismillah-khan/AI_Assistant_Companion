from fastapi import UploadFile

from app.voice.stt.whisper import WhisperClient


class VoiceService:
    def __init__(self) -> None:
        self.whisper = WhisperClient()

    async def transcribe(self, file: UploadFile) -> str:
        data = await file.read()
        return await self.whisper.transcribe_bytes(data)
