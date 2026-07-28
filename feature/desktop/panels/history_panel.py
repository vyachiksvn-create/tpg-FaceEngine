"""Desktop: History Panel"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus, HistoryManager


class HistoryPanel:
    def __init__(self, event_bus: "EventBus", history_mgr: "HistoryManager") -> None:
        self.event_bus = event_bus
        self.history_mgr = history_mgr

    def show_entries(self, entries: list) -> None:
        pass

    def filter(self, action: str | None = None) -> list:
        return []