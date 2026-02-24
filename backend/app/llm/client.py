import asyncio
import logging
from dataclasses import dataclass

import httpx

from app.core.config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResult:
    content: str
    tool_calls: list[dict]


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def chat(
        self,
        messages: list[dict[str, object]],
        tools: list[dict[str, object]] | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> LLMResult:
        if not self._settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required")

        payload: dict[str, object] = {
            "model": model or self._settings.llm_model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self._settings.llm_temperature,
            "max_tokens": self._settings.llm_max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        data = await self._post_json("/openai/v1/chat/completions", payload)
        message = data["choices"][0]["message"]
        return LLMResult(
            content=message.get("content") or "",
            tool_calls=message.get("tool_calls") or [],
        )

    async def _post_json(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        url = f"{self._settings.llm_api_base.rstrip('/')}{path}"
        headers = {
            "Authorization": f"Bearer {self._settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(1, self._settings.llm_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._settings.llm_timeout_seconds) as client:
                    response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError, KeyError) as exc:
                if attempt >= self._settings.llm_max_retries:
                    logger.exception("LLM request failed after retries")
                    raise
                backoff = 0.5 * (2 ** (attempt - 1))
                logger.warning("LLM request failed (attempt %s): %s", attempt, exc)
                await asyncio.sleep(backoff)

        raise RuntimeError("LLM request failed")
