from typing import Literal

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    goal: str
    model: str | None = None
    temperature: float | None = None
    max_steps: int | None = None


class PlanStep(BaseModel):
    id: int
    title: str
    description: str


class StepResult(BaseModel):
    id: int
    title: str
    status: Literal["pending", "running", "completed", "failed"]
    output: str | None = None
    error: str | None = None


class PlanResponse(BaseModel):
    goal: str
    steps: list[StepResult] = Field(default_factory=list)
    summary: str
    success: bool
