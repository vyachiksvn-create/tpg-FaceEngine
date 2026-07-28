"""Result Router: sort recognition results into workflow folders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from feature.desktop.processing_queue import QueueItem, QueueStatus


@dataclass
class RouteResult:
    item: QueueItem
    destination: Path | None = None
    reason: str | None = None


class ResultRouter:
    def __init__(self, base_root: Path, matches_root: Path, reject_root: Path, review_root: Path) -> None:
        self.base_root = Path(base_root)
        self.matches_root = Path(matches_root)
        self.reject_root = Path(reject_root)
        self.review_root = Path(review_root)

    def route(self, item: QueueItem, explanation: Any) -> RouteResult:
        if item.status == QueueStatus.REJECTED:
            return RouteResult(item=item, destination=self.reject_root, reason="rejected")
        if item.status == QueueStatus.UNKNOWN:
            return RouteResult(item=self.review_root / "Unknown", reason="unknown")
        if item.status == QueueStatus.NEW_PERSON:
            return RouteResult(item=self.review_root / "NewPersons", reason="new_person")
        if item.status == QueueStatus.CONFIRMED and item.identity_id is not None:
            identity_dir = self.base_root / str(item.identity_id)
            return RouteResult(item=item, destination=identity_dir, reason="confirmed")
        if item.status == QueueStatus.FOUND:
            identity_dir = self.matches_root / str(item.identity_id or "unknown")
            return RouteResult(item=item, destination=identity_dir, reason="found")
        return RouteResult(item=item, destination=self.review_root / "NeedConfirm", reason="need_confirm")
