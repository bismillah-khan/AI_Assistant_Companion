from app.agents.loop import AgentLoop
from app.core.config.settings import Settings
from app.llm.client import LLMClient
from app.llm.schemas import StructuredOutput
from app.models.chat import ChatRequest
from app.tools.registry import ToolRegistry


class AgentController:
    def __init__(self, tools: ToolRegistry, llm: LLMClient, settings: Settings) -> None:
        self.loop = AgentLoop(tools, llm, settings)

    async def run(self, request: ChatRequest) -> StructuredOutput:
        return await self.loop.run(request)
