"""Processing Queue: track photo states through operator workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class QueueStatus(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    FOUND = "found"
    CONFIRMED = "confirmed"
    NEW_PERSON = "new_person"
    UNKNOWN = "unknown"
    REJECTED = "rejected"
    ERROR = "error"


@dataclass
class QueueItem:
    path: Path
    status: QueueStatus = QueueStatus.WAITING
    identity_id: int | None = None
    distance: float | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str | None = None


class ProcessingQueue:
    def __init__(self) -> None:
        self.items: list[QueueItem] = []

    def add(self, path: Path) -> QueueItem:
        item = QueueItem(path=path)
        self.items.append(item)
        return item

    def get_next(self) -> QueueItem | None:
        for item in self.items:
            if item.status == QueueStatus.WAITING:
                item.status = QueueStatus.PROCESSING
                item.updated_at = datetime.utcnow()
                return item
        return None

    def update_status(self, path: Path, status: QueueStatus, **kwargs: Any) -> None:
        for item in self.items:
            if item.path == path:
                item.status = status
                item.updated_at = datetime.utcnow()
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                break

    def stats(self) -> dict[str, int]:
        stats: dict[str, int] = {}
        for item in self.items:
            stats[item.status.value] = stats.get(item.status.value, 0) + 1
        return stats
