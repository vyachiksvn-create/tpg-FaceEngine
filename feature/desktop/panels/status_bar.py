"""Desktop: Status Bar."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QStatusBar


class StatusBar:
    def __init__(self) -> None:
        self._status_bar: QStatusBar | None = None

    def set_message(self, message: str) -> None:
        pass

    def set_progress(self, current: int, total: int) -> None:
        pass

    def clear(self) -> None:
        pass