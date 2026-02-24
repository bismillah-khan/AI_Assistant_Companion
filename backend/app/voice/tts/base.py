from dataclasses import dataclass


AUDIO_MIME_TYPES: dict[str, str] = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "opus": "audio/opus",
}


@dataclass(frozen=True)
class TTSResult:
    audio_bytes: bytes
    media_type: str
    file_ext: str
