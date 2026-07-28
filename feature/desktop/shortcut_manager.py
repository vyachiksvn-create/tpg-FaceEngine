"""Desktop: Shortcut Manager."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from loguru import logger


@dataclass
class Shortcut:
    action: str
    keys: str
    description: str = ""


class ShortcutManager:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self._config_path = Path(config_path) if config_path else Path.cwd() / "shortcuts.json"
        self._shortcuts: dict[str, Shortcut] = {}
        self._handlers: dict[str, Callable[[], None]] = {}
        self._load_defaults()
        self._load()

    def _load_defaults(self) -> None:
        defaults = [
            Shortcut("confirm", "Enter", "Confirm current candidate"),
            Shortcut("new_person", "N", "Create new person"),
            Shortcut("skip", "S", "Skip photo"),
            Shortcut("delete", "Delete", "Delete photo"),
            Shortcut("focus_mode", "F", "Toggle focus mode"),
            Shortcut("desktop_mode", "Escape", "Switch to desktop mode"),
            Shortcut("next_candidate", "1", "Select candidate 1"),
            Shortcut("next_candidate_2", "2", "Select candidate 2"),
            Shortcut("next_candidate_3", "3", "Select candidate 3"),
            Shortcut("undo", "Ctrl+Z", "Undo last action"),
        ]
        for s in defaults:
            self._shortcuts[s.action] = s

    def _load(self) -> None:
        if not self._config_path.exists():
            return
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for action, keys in data.items():
                if action in self._shortcuts:
                    self._shortcuts[action].keys = keys
        except Exception as exc:
            logger.error(f"Failed to load shortcuts: {exc}")

    def save(self) -> None:
        data = {action: s.keys for action, s in self._shortcuts.items()}
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def bind(self, action: str, handler: Callable[[], None]) -> None:
        self._handlers[action] = handler

    def handle(self, keys: str) -> bool:
        for action, shortcut in self._shortcuts.items():
            if shortcut.keys.lower() == keys.lower():
                handler = self._handlers.get(action)
                if handler:
                    handler()
                    return True
        return False

    def get(self, action: str) -> Shortcut | None:
        return self._shortcuts.get(action)

    def list_shortcuts(self) -> list[Shortcut]:
        return list(self._shortcuts.values())