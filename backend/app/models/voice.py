from pydantic import BaseModel


class VoiceResponse(BaseModel):
    text: str


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    format: str | None = None
    stream: bool = False
