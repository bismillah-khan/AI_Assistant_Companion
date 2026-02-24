from fastapi import APIRouter, Depends

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("")
async def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    reply = await service.handle_chat(request)
    return ChatResponse(reply=reply, session_id=request.session_id)
