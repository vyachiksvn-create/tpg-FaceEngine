from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RecognitionPlugin(Protocol):
    name: str

    def detect_faces(self, image: Any) -> list[dict[str, Any]]: ...
    def get_embedding(self, image: Any, face: dict[str, Any]) -> Any: ...
    def load(self) -> None: ...
    def unload(self) -> None: ...


@runtime_checkable
class SearchPlugin(Protocol):
    name: str

    def add_vectors(self, vectors: Any, ids: list[int]) -> None: ...
    def search(self, query: Any, top_k: int) -> list[tuple[int, float]]: ...
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...
    def remove(self, ids: list[int]) -> None: ...


@dataclass
class PluginDescriptor:
    kind: str
    name: str
    plugin: Any
    version: str = "0.1.0"
    description: str = ""


class PluginManager:
    def __init__(self) -> None:
        self._registry: dict[str, dict[str, PluginDescriptor]] = {}

    def register_recognition(self, descriptor: PluginDescriptor) -> None:
        if descriptor.kind != "recognition":
            raise ValueError(f"Expected kind='recognition', got '{descriptor.kind}'")
        self._registry.setdefault("recognition", {})[descriptor.name] = descriptor
        logger.info(f"Recognition plugin registered: {descriptor.name}")

    def register_search(self, descriptor: PluginDescriptor) -> None:
        if descriptor.kind != "search":
            raise ValueError(f"Expected kind='search', got '{descriptor.kind}'")
        self._registry.setdefault("search", {})[descriptor.name] = descriptor
        logger.info(f"Search plugin registered: {descriptor.name}")

    def get_recognition(self, name: str) -> RecognitionPlugin:
        plugin = self._registry.get("recognition", {}).get(name)
        if plugin is None:
            raise ValueError(f"Recognition plugin '{name}' not found")
        if not isinstance(plugin.plugin, RecognitionPlugin):
            raise TypeError(f"Plugin '{name}' does not implement RecognitionPlugin")
        return plugin.plugin

    def get_search(self, name: str) -> SearchPlugin:
        plugin = self._registry.get("search", {}).get(name)
        if plugin is None:
            raise ValueError(f"Search plugin '{name}' not found")
        if not isinstance(plugin.plugin, SearchPlugin):
            raise TypeError(f"Plugin '{name}' does not implement SearchPlugin")
        return plugin.plugin

    def available_recognition(self) -> list[str]:
        return list(self._registry.get("recognition", {}).keys())

    def available_search(self) -> list[str]:
        return list(self._registry.get("search", {}).keys())

    def list_plugins(self) -> dict[str, list[PluginDescriptor]]:
        return {
            kind: [desc for desc in descriptors.values()]
            for kind, descriptors in self._registry.items()
        }

    def unregister(self, kind: str, name: str) -> None:
        if kind in self._registry and name in self._registry[kind]:
            del self._registry[kind][name]
            logger.info(f"Plugin unregistered: {kind}/{name}")

    def clear(self) -> None:
        self._registry.clear()