import inspect
import logging
from typing import Any

from pydantic import ValidationError

from app.security.audit import log_tool_allowed, log_tool_block
from app.tools.base import ToolDefinition
from app.tools.context import ToolContext

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register_tool(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        return self._tools[name]

    def list_tools(self) -> list[ToolDefinition]:
        return [self._tools[name] for name in sorted(self._tools.keys())]

    def openai_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self.list_tools()
        ]

    async def call(self, name: str, arguments: dict[str, Any], context: ToolContext) -> Any:
        try:
            tool = self.get(name)
        except KeyError:
            log_tool_block("tool_not_found", name, context.role)
            return {"error": "tool_not_found"}
        logger.info("tool_call name=%s arguments=%s", name, arguments)

        if tool.allowed_roles is not None and context.role not in tool.allowed_roles:
            log_tool_block("role_not_allowed", name, context.role)
            return {"error": "role_not_allowed"}

        if tool.permissions is not None:
            missing = set(tool.permissions) - context.permissions
            if missing:
                log_tool_block("permission_denied", name, context.role)
                return {"error": "permission_denied", "missing": sorted(missing)}

        if tool.dangerous and tool.requires_confirmation and name not in context.confirmed_tools:
            log_tool_block("confirmation_required", name, context.role)
            return {"error": "confirmation_required", "tool": name}

        try:
            parsed = tool.args_model.model_validate(arguments)
        except ValidationError as exc:
            logger.warning("tool_validation_failed name=%s error=%s", name, exc)
            return {"error": "tool_validation_failed", "details": exc.errors()}

        try:
            result = tool.handler(**parsed.model_dump())
            if inspect.isawaitable(result):
                result = await result
            log_tool_allowed(name, context.role)
            logger.info("tool_call_success name=%s", name)
            return result
        except Exception as exc:
            logger.exception("tool_call_failed name=%s", name)
            return {"error": "tool_execution_failed", "details": str(exc)}
