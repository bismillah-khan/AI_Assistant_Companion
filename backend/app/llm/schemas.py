from typing import Literal

from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    action: Literal["tool", "final"]
    reply: str
    tool_name: str | None = None
    tool_args: dict | None = None
    reasoning: list[str] = Field(default_factory=list)


class StructuredOutput(BaseModel):
    reply: str
    data: dict | None = None
    reasoning: list[str] = Field(default_factory=list)
