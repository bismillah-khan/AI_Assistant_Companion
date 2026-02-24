import json
import logging
from typing import Any

from app.core.config.settings import Settings
from app.core.errors import AppError
from app.llm.client import LLMClient
from app.models.planning import PlanRequest, PlanStep, PlanResponse, StepResult

logger = logging.getLogger(__name__)


class PlanningAgent:
    def __init__(self, llm: LLMClient, settings: Settings) -> None:
        self.llm = llm
        self.settings = settings

    async def run(self, request: PlanRequest) -> PlanResponse:
        steps = await self._create_plan(request)
        results: list[StepResult] = []
        success = True

        for step in steps:
            # Execute steps sequentially and stop on failure.
            result = await self._execute_step(request, step)
            results.append(result)
            if result.status == "failed":
                success = False
                break

        summary = await self._summarize(request.goal, results)
        return PlanResponse(goal=request.goal, steps=results, summary=summary, success=success)

    async def _create_plan(self, request: PlanRequest) -> list[PlanStep]:
        prompt = (
            "You are a planner. Break the goal into ordered, minimal steps. "
            "Return JSON only: {\"steps\": [{\"title\": \"...\", \"description\": \"...\"}]}."
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": request.goal},
        ]

        result = await self.llm.chat(
            messages=messages,
            tools=None,
            model=request.model,
            temperature=request.temperature or self.settings.planning_temperature,
        )

        try:
            payload = json.loads(result.content)
            raw_steps = payload.get("steps", [])
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("invalid_plan_json: %s", exc)
            raise AppError("invalid_plan_json", status_code=500) from exc

        max_steps = request.max_steps or self.settings.planning_max_steps
        steps: list[PlanStep] = []
        for index, item in enumerate(raw_steps[:max_steps], start=1):
            title = str(item.get("title", f"Step {index}"))
            description = str(item.get("description", ""))
            steps.append(PlanStep(id=index, title=title, description=description))

        if not steps:
            raise AppError("empty_plan", status_code=500)
        return steps

    async def _execute_step(self, request: PlanRequest, step: PlanStep) -> StepResult:
        prompt = (
            "You are executing a plan step. Return JSON only: "
            '{"status": "completed|failed", "output": "...", "error": "...|null"}. '
            "Keep output concise."
        )
        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Goal: {request.goal}\nStep: {step.title}\nDetails: {step.description}",
            },
        ]

        result = await self.llm.chat(
            messages=messages,
            tools=None,
            model=request.model,
            temperature=request.temperature or self.settings.planning_temperature,
        )

        try:
            payload = json.loads(result.content)
            status = payload.get("status", "failed")
            output = payload.get("output")
            error = payload.get("error")
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("invalid_step_json: %s", exc)
            return StepResult(id=step.id, title=step.title, status="failed", error="invalid_step_json")

        if status not in {"completed", "failed"}:
            status = "failed"

        return StepResult(
            id=step.id,
            title=step.title,
            status=status,
            output=str(output) if output is not None else None,
            error=str(error) if error else None,
        )

    async def _summarize(self, goal: str, results: list[StepResult]) -> str:
        # Summarize results even if partial.
        summary_prompt = (
            "Summarize the plan execution in 2-4 sentences. "
            "Mention completed steps and any failures."
        )
        lines = [f"Goal: {goal}"]
        for item in results:
            lines.append(f"Step {item.id} {item.title}: {item.status}")
            if item.error:
                lines.append(f"Error: {item.error}")

        messages = [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": "\n".join(lines)},
        ]

        result = await self.llm.chat(messages=messages, tools=None)
        return result.content.strip() or "Execution summary unavailable."
