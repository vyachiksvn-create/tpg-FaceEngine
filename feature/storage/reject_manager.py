"""Rejection tracking for archive import."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RejectionRecord:
    path: Path
    reason: str
    details: str | None = None


@dataclass
class RejectStats:
    total_rejected: int = 0
    by_reason: dict[str, int] = field(default_factory=dict)
    records: list[RejectionRecord] = field(default_factory=list)

    def add(self, path: Path, reason: str, details: str | None = None) -> None:
        self.total_rejected += 1
        self.by_reason[reason] = self.by_reason.get(reason, 0) + 1
        self.records.append(RejectionRecord(path=path, reason=reason, details=details))

    def get_records(self, reason: str | None = None) -> list[RejectionRecord]:
        if reason is None:
            return list(self.records)
        return [r for r in self.records if r.reason == reason]


class RejectManager:
    def __init__(self) -> None:
        self.stats = RejectStats()

    def record(self, path: Path, reason: str, details: str | None = None) -> None:
        self.stats.add(path, reason, details)

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_rejected": self.stats.total_rejected,
            "by_reason": dict(self.stats.by_reason),
            "records": [
                {
                    "path": str(r.path),
                    "reason": r.reason,
                    "details": r.details,
                }
                for r in self.stats.records
            ],
        }

    def summary(self) -> dict[str, int]:
        return dict(self.stats.by_reason)
