from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolContext:
    role: str = "user"
    confirmed_tools: set[str] = field(default_factory=set)
    permissions: set[str] = field(default_factory=set)
