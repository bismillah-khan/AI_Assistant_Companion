from dataclasses import dataclass

from app.core.errors import AppError
from app.plugins.schema import PluginManifest


@dataclass(frozen=True)
class PluginRecord:
    name: str
    version: str


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginRecord] = {}

    def register(self, manifest: PluginManifest) -> None:
        existing = self._plugins.get(manifest.name)
        if existing and not _is_newer(manifest.version, existing.version):
            raise AppError("plugin_version_conflict", status_code=400)
        self._plugins[manifest.name] = PluginRecord(name=manifest.name, version=manifest.version)


def _is_newer(candidate: str, current: str) -> bool:
    return _parse_version(candidate) >= _parse_version(current)


def _parse_version(value: str) -> tuple[int, ...]:
    parts = value.split(".")
    numbers: list[int] = []
    for part in parts:
        try:
            numbers.append(int(part))
        except ValueError:
            numbers.append(0)
    return tuple(numbers)
