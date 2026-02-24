from app.tools.registry import ToolRegistry


class AgentController:
    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    async def run(self, message: str, session_id: str | None) -> str:
        # Placeholder for tool-calling LLM loop
        tools = ", ".join(self.tools.list_tools())
        suffix = f" (tools: {tools})" if tools else ""
        session = session_id or "new"
        return f"echo:{message} session:{session}{suffix}"
