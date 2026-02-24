from fastapi import APIRouter, Depends, UploadFile, File

from app.models.voice import VoiceResponse
from app.services.voice_service import VoiceService

router = APIRouter()


def get_voice_service() -> VoiceService:
    return VoiceService()


@router.post("")
async def voice(file: UploadFile = File(...), service: VoiceService = Depends(get_voice_service)) -> VoiceResponse:
    text = await service.transcribe(file)
    return VoiceResponse(text=text)
