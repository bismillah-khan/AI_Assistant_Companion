from fastapi import APIRouter

from app.api.v1.chat.router import router as chat_router
from app.api.v1.voice.router import router as voice_router
from app.api.v1.health.router import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(voice_router, prefix="/voice", tags=["voice"])
