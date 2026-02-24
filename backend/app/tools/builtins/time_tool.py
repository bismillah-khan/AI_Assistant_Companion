from datetime import datetime, timezone

from pydantic import BaseModel

from app.tools.base import ToolDefinition


class GetUtcTimeArgs(BaseModel):
    pass


def get_utc_time() -> dict:
    return {"utc": datetime.now(timezone.utc).isoformat()}


TOOL = ToolDefinition(
    name="get_utc_time",
    description="Get current UTC time in ISO-8601 format.",
    args_model=GetUtcTimeArgs,
    handler=get_utc_time,
)
