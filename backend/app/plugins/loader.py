import json
import logging
from pathlib import Path
from typing import Iterable

from app.core.config.settings import Settings
from app.plugins.executor import execute_tool
from app.plugins.registry import PluginRegistry
from app.plugins.schema import PluginManifest
from app.tools.base import ToolDefinition
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def load_plugins(registry: ToolRegistry, settings: Settings) -> None:
    if not settings.plugins_enabled:
        return

    base_dir = Path(settings.plugins_dir)
    if not base_dir.exists():
        logger.info("plugins_dir_missing path=%s", base_dir)
        return

    plugin_registry = PluginRegistry()
    for manifest_path in _iter_manifests(base_dir):
        manifest = _load_manifest(manifest_path)
        if not manifest.enabled:
            continue

        try:
            plugin_registry.register(manifest)
            _register_plugin_tools(registry, settings, manifest, manifest_path.parent)
        except Exception as exc:
            logger.exception("plugin_load_failed path=%s error=%s", manifest_path, exc)


def _iter_manifests(base_dir: Path) -> Iterable[Path]:
    return base_dir.glob("*/manifest.json")


def _load_manifest(path: Path) -> PluginManifest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return PluginManifest.model_validate(payload)


def _register_plugin_tools(
    registry: ToolRegistry,
    settings: Settings,
    manifest: PluginManifest,
    plugin_dir: Path,
) -> None:
    entry_path = plugin_dir / manifest.entry
    for tool in manifest.tools:
        if tool.permissions and not set(tool.permissions).issubset(set(manifest.permissions)):
            logger.warning("plugin_permission_mismatch plugin=%s tool=%s", manifest.name, tool.name)
            continue

        timeout = tool.timeout_seconds or settings.plugin_exec_timeout_seconds
        handler = _make_handler(entry_path, tool.name, timeout)
        registry.register_tool(
            ToolDefinition(
                name=f"{manifest.name}.{tool.name}",
                description=tool.description,
                args_model=_make_args_model(tool.parameters),
                handler=handler,
                dangerous=tool.dangerous,
                allowed_roles=tool.allowed_roles,
                requires_confirmation=tool.requires_confirmation,
                permissions=tool.permissions,
            )
        )


def _make_handler(entry_path: Path, tool_name: str, timeout: float):
    def _handler(**kwargs):
        return execute_tool(entry_path, tool_name, kwargs, timeout)

    return _handler


def _make_args_model(schema: dict):
    from pydantic import create_model
    from pydantic.config import ConfigDict

    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields = {name: (_map_type(spec), ... if name in required else None) for name, spec in props.items()}
    return create_model("PluginArgs", __config__=ConfigDict(extra="allow"), **fields)


def _map_type(spec: dict):
    json_type = spec.get("type")
    if json_type == "string":
        return str
    if json_type == "integer":
        return int
    if json_type == "number":
        return float
    if json_type == "boolean":
        return bool
    if json_type == "array":
        return list
    if json_type == "object":
        return dict
    return object
