from uuid import uuid4
import asyncio

from app.agents.controller import AgentController
from app.core.config.settings import get_settings
from app.llm.client import LLMClient
from app.llm.schemas import StructuredOutput
from app.memory.short_term.conversation import ConversationMemory
from app.models.chat import ChatRequest
from app.models.chat import ChatMessage
from app.rag.service import RAGService
from app.security.validation import validate_user_input
from app.tools.loader import load_builtin_tools
from app.plugins.loader import load_plugins
from app.tools.registry import ToolRegistry


class ChatService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.tools = ToolRegistry()
        load_builtin_tools(self.tools)
        load_plugins(self.tools, self.settings)
        self.llm = LLMClient(self.settings)
        self.agent = AgentController(self.tools, self.llm, self.settings)
        self.memory = ConversationMemory(self.settings)
        self.rag = RAGService(self.settings)

    async def handle_chat(self, request: ChatRequest) -> tuple[StructuredOutput, str]:
        session_id = request.session_id or str(uuid4())
        validate_user_input(request.message)
        
        # Try to get history from MongoDB, but don't fail if unavailable
        history = []
        try:
            history = await asyncio.wait_for(
                self.memory.get_history(session_id),
                timeout=2.0
            )
        except (Exception, asyncio.TimeoutError):
            # MongoDB not available or timeout, use empty history
            pass
        
        # Try to get RAG context, but don't fail if unavailable
        try:
            context = await asyncio.wait_for(
                self.rag.retrieve_context(request.message),
                timeout=2.0
            )
            if context:
                history = [ChatMessage(role="system", name="rag_context", content=f"Context:\n{context}")] + history
        except (Exception, asyncio.TimeoutError):
            # RAG not available or timeout, skip context
            pass
            
        request.history = history

        output = await self.agent.run(request)

        # Try to save to MongoDB, but don't fail if unavailable
        try:
            await asyncio.wait_for(
                self.memory.append_messages(
                    session_id,
                    [
                        ChatMessage(role="user", content=request.message),
                        ChatMessage(role="assistant", content=output.reply),
                    ],
                ),
                timeout=2.0
            )
        except (Exception, asyncio.TimeoutError):
            # MongoDB not available or timeout, skip saving
            pass

        return output, session_id
