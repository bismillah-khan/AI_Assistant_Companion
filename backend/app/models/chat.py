from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None
    tool_call_id: str | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    history: list[ChatMessage] = Field(default_factory=list)
    model: str | None = None
    temperature: float | None = None
    role: str = "user"
    confirmed_tools: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    session_id: str | None = None
    structured: dict | None = None
    reasoning: list[str] = Field(default_factory=list)
