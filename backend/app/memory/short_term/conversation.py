from datetime import datetime, timezone
from typing import Iterable

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config.settings import Settings
from app.db.mongo.client import get_mongo_client
from app.models.chat import ChatMessage


class ConversationMemory:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient = get_mongo_client()
        self._collection = self._client[settings.mongo_db]["chat_messages"]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("session_id")
        await self._collection.create_index("created_at")

    async def get_history(self, session_id: str) -> list[ChatMessage]:
        cursor = (
            self._collection.find({"session_id": session_id})
            .sort("created_at", -1)
            .limit(self._settings.memory_max_messages)
        )
        items = [self._doc_to_message(doc) async for doc in cursor]
        return list(reversed(items))

    async def append_messages(self, session_id: str, messages: Iterable[ChatMessage]) -> None:
        docs = [self._message_to_doc(session_id, message) for message in messages]
        if docs:
            await self._collection.insert_many(docs)
            await self._trim_excess(session_id)

    async def _trim_excess(self, session_id: str) -> None:
        cursor = (
            self._collection.find({"session_id": session_id})
            .sort("created_at", -1)
            .skip(self._settings.memory_max_messages)
            .project({"_id": 1})
        )
        ids = [doc["_id"] async for doc in cursor]
        if ids:
            await self._collection.delete_many({"_id": {"$in": ids}})

    @staticmethod
    def _message_to_doc(session_id: str, message: ChatMessage) -> dict:
        return {
            "session_id": session_id,
            "role": message.role,
            "content": message.content,
            "name": message.name,
            "tool_call_id": message.tool_call_id,
            "created_at": datetime.now(timezone.utc),
        }

    @staticmethod
    def _doc_to_message(doc: dict) -> ChatMessage:
        return ChatMessage(
            role=doc["role"],
            content=doc["content"],
            name=doc.get("name"),
            tool_call_id=doc.get("tool_call_id"),
        )
