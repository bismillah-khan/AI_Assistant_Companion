import json
import logging
from dataclasses import dataclass

from app.core.config.settings import Settings
from app.core.errors import AppError
from app.llm.client import LLMClient
from app.llm.schemas import AgentDecision, StructuredOutput
from app.models.chat import ChatRequest
from app.tools.context import ToolContext
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentStep:
    index: int
    action: str
    tool_name: str | None
    observation: dict | None
    reasoning: list[str]


class AgentLoop:
    def __init__(self, tools: ToolRegistry, llm: LLMClient, settings: Settings) -> None:
        self.tools = tools
        self.llm = llm
        self.settings = settings

    async def run(self, request: ChatRequest) -> StructuredOutput:
        messages = self._build_messages(request)
        steps: list[AgentStep] = []
        context = ToolContext(
            role=request.role,
            confirmed_tools=set(request.confirmed_tools),
            permissions=set(request.permissions),
        )

        for index in range(self.settings.agent_max_iterations):
            # Each iteration: LLM decision -> optional tool -> observation.
            decision = await self._decide(messages, request)

            if decision.action == "final":
                return StructuredOutput(
                    reply=decision.reply,
                    data={"steps": [step.__dict__ for step in steps]},
                    reasoning=decision.reasoning,
                )

            if decision.action != "tool":
                raise AppError("invalid_agent_action", status_code=500)

            if not decision.tool_name:
                raise AppError("tool_call_missing_name", status_code=400)

            observation = await self._execute_tool(decision.tool_name, decision.tool_args or {}, context)
            steps.append(
                AgentStep(
                    index=index,
                    action=decision.action,
                    tool_name=decision.tool_name,
                    observation=observation if isinstance(observation, dict) else {"result": observation},
                    reasoning=decision.reasoning,
                )
            )

            messages.append({"role": "assistant", "content": self._serialize_decision(decision)})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": f"tool-{index}",
                    "content": self._serialize_tool_result(observation),
                }
            )

        logger.warning("agent_loop_max_iterations_reached")
        # Safe exit: return a final response when iteration limit is hit.
        return StructuredOutput(
            reply="Unable to complete within the iteration limit.",
            data={"error": "max_iterations", "steps": [step.__dict__ for step in steps]},
            reasoning=[],
        )

    async def _decide(self, messages: list[dict[str, object]], request: ChatRequest) -> AgentDecision:
        result = await self.llm.chat(
            messages=messages,
            tools=None,
            model=request.model,
            temperature=request.temperature,
        )
        logger.info(f"LLM response content: {result.content[:500]}")  # Log first 500 chars
        try:
            payload = json.loads(result.content)
            logger.info(f"Parsed JSON payload: {payload}")
            return AgentDecision.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error(f"Failed to parse LLM response. Content: {result.content}")
            logger.warning("invalid_agent_decision_json: %s", exc)
            # Return a fallback response instead of failing
            return AgentDecision(
                action="final",
                reply=result.content if result.content else "I apologize, but I encountered an error processing your request.",
                tool_name=None,
                tool_args=None,
                reasoning=["Fallback due to JSON parsing error"]
            )

    def _build_messages(self, request: ChatRequest) -> list[dict[str, object]]:
        messages: list[dict[str, object]] = [
            {
                "role": "system",
                "content": self._system_prompt(),
            }
        ]

        for item in request.history:
            if item.role == "system" and item.name != "rag_context":
                continue
            payload: dict[str, object] = {"role": item.role, "content": item.content}
            if item.name:
                payload["name"] = item.name
            if item.tool_call_id:
                payload["tool_call_id"] = item.tool_call_id
            messages.append(payload)

        messages.append({"role": "user", "content": request.message})
        return messages

    async def _execute_tool(self, name: str, args: dict, context: ToolContext) -> object:
        # Tool execution is validated and wrapped in the registry.
        return await self.tools.call(name, args, context)

    def _system_prompt(self) -> str:
        return (
            f"{self.settings.system_prompt}\n"
            "You must respond with valid JSON only, following this exact schema:\n"
            '{"action": "tool" or "final", "reply": "your response text", "tool_name": null or "tool_name", '
            '"tool_args": null or {...}, "reasoning": ["step1", "step2", ...]}.\n'
            'When action="tool", you MUST provide both tool_name and tool_args.\n'
            'When action="final", set tool_name and tool_args to null and provide your final answer in reply.'
        )

    @staticmethod
    def _serialize_decision(decision: AgentDecision) -> str:
        return json.dumps(decision.model_dump(), ensure_ascii=True)

    @staticmethod
    def _serialize_tool_result(result: object) -> str:
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=True)
