from fastapi import APIRouter, Depends, Request

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("")
async def chat(
    request: ChatRequest,
    http_request: Request,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    header_role = http_request.headers.get("x-client-role")
    if header_role:
        request.role = header_role

    confirm_header = http_request.headers.get("x-confirm-tools")
    if confirm_header:
        confirmed = [item.strip() for item in confirm_header.split(",") if item.strip()]
        request.confirmed_tools = sorted(set(request.confirmed_tools + confirmed))

    permissions_header = http_request.headers.get("x-client-permissions")
    if permissions_header:
        permissions = [item.strip() for item in permissions_header.split(",") if item.strip()]
        request.permissions = sorted(set(request.permissions + permissions))

    output, session_id = await service.handle_chat(request)
    return ChatResponse(
        reply=output.reply,
        session_id=session_id,
        structured=output.data,
        reasoning=output.reasoning,
    )
