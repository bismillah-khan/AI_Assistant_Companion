from app.agents.planning.planner import PlanningAgent
from app.core.config.settings import get_settings
from app.llm.client import LLMClient
from app.models.planning import PlanRequest, PlanResponse
from app.security.validation import validate_user_input


class PlanningService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMClient(self.settings)
        self.agent = PlanningAgent(self.llm, self.settings)

    async def run(self, request: PlanRequest) -> PlanResponse:
        validate_user_input(request.goal)
        return await self.agent.run(request)
