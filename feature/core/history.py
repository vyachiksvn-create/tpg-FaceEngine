from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Sequence

from loguru import logger


class ActionType(str, Enum):
    IMPORT = "import"
    IDENTITY_CREATE = "identity_create"
    IDENTITY_UPDATE = "identity_update"
    IDENTITY_MERGE = "identity_merge"
    PHOTO_ADD = "photo_add"
    PHOTO_REMOVE = "photo_remove"
    PHOTO_UPDATE = "photo_update"
    PHOTO_PRIMARY = "photo_primary"
    PROFILE_CHANGE = "profile_change"
    WORKSPACE_SWITCH = "workspace_switch"
    BACKUP = "backup"
    RESTORE = "restore"
    SYSTEM = "system"


@dataclass
class HistoryEntry:
    action: ActionType
    entity_type: str
    entity_id: int | None
    description: str
    timestamp: float = field(default_factory=time.time)
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    user: str | None = None
    snapshot_before: dict[str, Any] | None = None
    snapshot_after: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "description": self.description,
            "timestamp": self.timestamp,
            "entry_id": self.entry_id,
            "user": self.user,
            "snapshot_before": self.snapshot_before,
            "snapshot_after": self.snapshot_after,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoryEntry:
        return cls(
            action=ActionType(data["action"]),
            entity_type=data["entity_type"],
            entity_id=data.get("entity_id"),
            description=data.get("description", ""),
            timestamp=data.get("timestamp", time.time()),
            entry_id=data.get("entry_id", uuid.uuid4().hex),
            user=data.get("user"),
            snapshot_before=data.get("snapshot_before"),
            snapshot_after=data.get("snapshot_after"),
            metadata=data.get("metadata", {}),
        )


class HistoryManager:
    def __init__(self, history_dir: str | Path | None = None, max_entries: int = 100000) -> None:
        self._history_dir = Path(history_dir) if history_dir else Path.cwd() / "history"
        self._history_dir.mkdir(parents=True, exist_ok=True)
        self._max_entries = max_entries
        self._current_session: str | None = None
        self._buffer: list[HistoryEntry] = []

    def start_session(self, session_id: str | None = None) -> str:
        self._current_session = session_id or uuid.uuid4().hex
        self._buffer.clear()
        logger.info(f"History session started: {self._current_session}")
        return self._current_session

    def record(self, entry: HistoryEntry) -> None:
        if self._current_session:
            entry.metadata.setdefault("session_id", self._current_session)
        self._buffer.append(entry)
        logger.debug(f"History recorded: {entry.action.value} - {entry.description}")

    def flush(self) -> None:
        if not self._buffer:
            return
        entries = self._buffer
        self._buffer = []
        self._write(entries)

    def _write(self, entries: Sequence[HistoryEntry]) -> None:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_path = self._history_dir / f"{today}.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def query(
        self,
        action: ActionType | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        since: float | None = None,
        limit: int = 100,
    ) -> list[HistoryEntry]:
        results: list[HistoryEntry] = []
        for log_path in sorted(self._history_dir.glob("*.jsonl")):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        if action and data.get("action") != action.value:
                            continue
                        if entity_type and data.get("entity_type") != entity_type:
                            continue
                        if entity_id is not None and data.get("entity_id") != entity_id:
                            continue
                        if since is not None and data.get("timestamp", 0) < since:
                            continue
                        results.append(HistoryEntry.from_dict(data))
                        if len(results) >= limit:
                            return results
            except Exception as exc:
                logger.error(f"Failed to read history file {log_path}: {exc}")
        return results

    def last(self, entity_type: str, entity_id: int) -> HistoryEntry | None:
        entries = self.query(entity_type=entity_type, entity_id=entity_id, limit=1)
        return entries[0] if entries else None

    def rollback(self, entry: HistoryEntry) -> bool:
        if entry.snapshot_before is None:
            logger.warning(f"Cannot rollback entry {entry.entry_id}: no snapshot")
            return False
        logger.info(f"Rolling back entry {entry.entry_id}")
        self.record(HistoryEntry(
            action=ActionType.SYSTEM,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            description=f"Rollback of {entry.entry_id}",
            snapshot_before=entry.snapshot_after,
            snapshot_after=entry.snapshot_before,
        ))
        return True