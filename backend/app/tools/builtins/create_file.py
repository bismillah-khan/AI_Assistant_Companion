from pathlib import Path

from pydantic import BaseModel, Field

from app.tools.base import ToolDefinition


class CreateFileArgs(BaseModel):
    path: str = Field(..., description="Relative file path")
    content: str = Field("", description="File contents")
    overwrite: bool = Field(False, description="Allow overwriting existing file")


def create_file(path: str, content: str = "", overwrite: bool = False) -> dict:
    base_dir = Path.cwd() / "tool_workspace"
    base_dir.mkdir(parents=True, exist_ok=True)

    target = (base_dir / path).resolve()
    if base_dir not in target.parents and target != base_dir:
        return {"status": "blocked", "reason": "path_outside_workspace"}

    if target.exists() and not overwrite:
        return {"status": "skipped", "reason": "file_exists", "path": str(target)}

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"status": "created", "path": str(target)}


TOOL = ToolDefinition(
    name="create_file",
    description="Create a file in the tool workspace directory.",
    args_model=CreateFileArgs,
    handler=create_file,
    dangerous=True,
    allowed_roles=["admin"],
    requires_confirmation=True,
)
