"""Core: Capability Manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Capabilities:
    recognition: bool = True
    history: bool = True
    inspector: bool = False
    ai_assistant: bool = False
    workflow_builder: bool = False
    benchmark: bool = False
    plugin_marketplace: bool = False
    focus_mode: bool = True
    shortcuts: bool = True
    themes: bool = True


class CapabilityManager:
    def __init__(self, capabilities: Capabilities | None = None) -> None:
        self._capabilities = capabilities or Capabilities()

    def enable(self, name: str) -> None:
        if hasattr(self._capabilities, name):
            setattr(self._capabilities, name, True)

    def disable(self, name: str) -> None:
        if hasattr(self._capabilities, name):
            setattr(self._capabilities, name, False)

    def is_enabled(self, name: str) -> bool:
        return getattr(self._capabilities, name, False)

    @property
    def capabilities(self) -> Capabilities:
        return self._capabilities