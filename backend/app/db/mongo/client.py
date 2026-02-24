from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config.settings import get_settings


def get_mongo_client() -> AsyncIOMotorClient:
    settings = get_settings()
    return AsyncIOMotorClient(settings.mongo_uri)
