from typing import Any

from pydantic import BaseModel, Field


class PluginToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    dangerous: bool = False
    allowed_roles: list[str] | None = None
    requires_confirmation: bool = False
    permissions: list[str] | None = None
    timeout_seconds: float | None = None


class PluginManifest(BaseModel):
    name: str
    version: str
    entry: str
    enabled: bool = True
    permissions: list[str] = Field(default_factory=list)
    tools: list[PluginToolSpec] = Field(default_factory=list)
    isolation: bool = True
