from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Type

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    args_model: Type[BaseModel]
    handler: Callable[..., Awaitable[Any]] | Callable[..., Any]
    dangerous: bool = False
    allowed_roles: list[str] | None = None
    requires_confirmation: bool = False
    permissions: list[str] | None = None

    @property
    def parameters(self) -> dict[str, Any]:
        return self.args_model.model_json_schema()
