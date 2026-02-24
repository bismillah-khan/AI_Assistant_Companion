from app.agents.controller import AgentController
from app.models.chat import ChatRequest
from app.tools.registry import ToolRegistry


class ChatService:
    def __init__(self) -> None:
        self.tools = ToolRegistry()
        self.agent = AgentController(self.tools)

    async def handle_chat(self, request: ChatRequest) -> str:
        return await self.agent.run(request.message, request.session_id)
