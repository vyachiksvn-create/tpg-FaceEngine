"""Desktop: RecognitionSession for stats and timing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionStats:
    total_photos: int = 0
    processed: int = 0
    confirmed: int = 0
    skipped: int = 0
    new_persons: int = 0
    errors: int = 0
    avg_time_ms: float = 0.0
    total_time_ms: float = 0.0


class RecognitionSession:
    def __init__(self) -> None:
        self._stats = SessionStats()
        self._started_at: float | None = None
        self._finished_at: float | None = None
        self._processing_times: list[float] = []

    def start(self) -> None:
        self._started_at = time.time()
        self._stats = SessionStats()

    def finish(self) -> None:
        self._finished_at = time.time()

    def record(self, processing_time_ms: float, result: str) -> None:
        self._stats.processed += 1
        self._stats.total_time_ms += processing_time_ms
        self._processing_times.append(processing_time_ms)
        if self._processing_times:
            self._stats.avg_time_ms = sum(self._processing_times) / len(self._processing_times)
        if result == "confirmed":
            self._stats.confirmed += 1
        elif result == "skipped":
            self._stats.skipped += 1
        elif result == "new_person":
            self._stats.new_persons += 1
        elif result == "error":
            self._stats.errors += 1

    def set_total(self, total: int) -> None:
        self._stats.total_photos = total

    @property
    def stats(self) -> SessionStats:
        return self._stats

    @property
    def is_running(self) -> bool:
        return self._started_at is not None and self._finished_at is None