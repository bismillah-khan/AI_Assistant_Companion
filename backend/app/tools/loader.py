import importlib
import logging
import pkgutil
from types import ModuleType
from typing import Iterable

from app.tools.base import ToolDefinition
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def load_builtin_tools(registry: ToolRegistry, package: str = "app.tools.builtins") -> None:
    for module in _iter_modules(package):
        _register_from_module(registry, module)


def _iter_modules(package: str) -> Iterable[ModuleType]:
    root = importlib.import_module(package)
    for info in pkgutil.iter_modules(root.__path__, root.__name__ + "."):
        module = importlib.import_module(info.name)
        yield module


def _register_from_module(registry: ToolRegistry, module: ModuleType) -> None:
    if hasattr(module, "TOOL"):
        tool = getattr(module, "TOOL")
        _register_tool(registry, tool, module.__name__)
    if hasattr(module, "TOOLS"):
        tools = getattr(module, "TOOLS")
        for tool in tools:
            _register_tool(registry, tool, module.__name__)


def _register_tool(registry: ToolRegistry, tool: ToolDefinition, module_name: str) -> None:
    if not isinstance(tool, ToolDefinition):
        logger.warning("Skipping invalid tool in %s", module_name)
        return
    registry.register_tool(tool)
