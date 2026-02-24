from pydantic import BaseModel, Field

from app.tools.base import ToolDefinition


class OpenApplicationArgs(BaseModel):
    name: str = Field(..., description="Application name to open")


def open_application(name: str) -> dict:
    return {
        "status": "blocked",
        "reason": "Server-side tool cannot open local applications.",
        "requested": name,
    }


TOOL = ToolDefinition(
    name="open_application",
    description="Open a local application by name.",
    args_model=OpenApplicationArgs,
    handler=open_application,
    dangerous=True,
    allowed_roles=["admin"],
    requires_confirmation=True,
)
