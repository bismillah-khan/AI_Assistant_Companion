from pydantic import BaseModel, Field

from app.tools.base import ToolDefinition


class SearchWebArgs(BaseModel):
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, ge=1, le=10, description="Max results to return")


def search_web(query: str, top_k: int = 5) -> dict:
    _ = top_k
    return {"query": query, "results": []}


TOOL = ToolDefinition(
    name="search_web",
    description="Search the web for recent information.",
    args_model=SearchWebArgs,
    handler=search_web,
)
