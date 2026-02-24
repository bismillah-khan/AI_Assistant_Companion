from typing import Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., object]] = {}

    def register(self, name: str, func: Callable[..., object]) -> None:
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[name] = func

    def get(self, name: str) -> Callable[..., object]:
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())
