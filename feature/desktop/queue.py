"""Desktop: Queue Model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QueueItemStatus(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    FOUND = "found"
    CONFIRMED = "confirmed"
    NEW_PERSON = "new_person"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class QueueItem:
    item_id: str
    file_path: str
    status: QueueItemStatus = QueueItemStatus.WAITING
    candidates: list[dict[str, Any]] = field(default_factory=list)
    selected_identity_id: int | None = None
    error: str | None = None
    created_at: float = field(default_factory=lambda: __import__("time").time())


class QueueModel:
    def __init__(self) -> None:
        self._items: dict[str, QueueItem] = {}

    def add(self, item: QueueItem) -> None:
        self._items[item.item_id] = item

    def get(self, item_id: str) -> QueueItem | None:
        return self._items.get(item_id)

    def update_status(self, item_id: str, status: QueueItemStatus) -> bool:
        item = self._items.get(item_id)
        if not item:
            return False
        item.status = status
        return True

    def pending(self) -> list[QueueItem]:
        return [item for item in self._items.values() if item.status == QueueItemStatus.WAITING]

    def processing(self) -> list[QueueItem]:
        return [item for item in self._items.values() if item.status == QueueItemStatus.PROCESSING]

    def all(self) -> list[QueueItem]:
        return list(self._items.values())