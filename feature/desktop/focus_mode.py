"""Desktop: Focus Mode for operator workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FocusMode(str, Enum):
    DESKTOP = "desktop"
    FOCUS = "focus"


@dataclass
class FocusState:
    mode: FocusMode = FocusMode.DESKTOP
    current_photo_index: int = 0
    total_photos: int = 0
    confirmed: int = 0
    skipped: int = 0
    new_persons: int = 0
    errors: int = 0
    session_started_at: float = field(default_factory=lambda: __import__("time").time())


class FocusModeController:
    def __init__(self) -> None:
        self._state = FocusState()

    def enter_focus_mode(self) -> None:
        self._state.mode = FocusMode.FOCUS

    def exit_focus_mode(self) -> None:
        self._state.mode = FocusMode.DESKTOP

    def next_photo(self) -> None:
        self._state.current_photo_index += 1

    def record_result(self, result: str) -> None:
        if result == "confirmed":
            self._state.confirmed += 1
        elif result == "skipped":
            self._state.skipped += 1
        elif result == "new_person":
            self._state.new_persons += 1
        elif result == "error":
            self._state.errors += 1

    def reset_session(self) -> None:
        self._state = FocusState()

    @property
    def state(self) -> FocusState:
        return self._state