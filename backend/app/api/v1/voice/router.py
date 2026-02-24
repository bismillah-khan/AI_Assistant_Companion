from fastapi import APIRouter, Depends, UploadFile, File, Response
from fastapi.responses import StreamingResponse

from app.models.voice import TTSRequest, VoiceResponse
from app.services.tts_service import TTSService
from app.services.voice_service import VoiceService

router = APIRouter()


def get_voice_service() -> VoiceService:
    return VoiceService()


def get_tts_service() -> TTSService:
    return TTSService()


@router.post("")
async def voice(file: UploadFile = File(...), service: VoiceService = Depends(get_voice_service)) -> VoiceResponse:
    text = await service.transcribe(file)
    return VoiceResponse(text=text)


@router.post("/tts")
async def tts(request: TTSRequest, service: TTSService = Depends(get_tts_service)) -> Response:
    stream = await service.stream(request)
    if stream is not None:
        iterator, media_type = stream
        return StreamingResponse(iterator, media_type=media_type)

    result = await service.synthesize(request)
    return Response(content=result.audio_bytes, media_type=result.media_type)
