"""Inbox Manager: scan and register incoming photos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class InboxItem:
    path: Path
    size_bytes: int = 0


class InboxManager:
    def __init__(self, inbox_root: Path) -> None:
        self.inbox_root = Path(inbox_root)

    def scan(self) -> list[InboxItem]:
        if not self.inbox_root.exists():
            logger.warning(f"Inbox not found: {self.inbox_root}")
            return []
        items = []
        for p in self.inbox_root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                items.append(InboxItem(path=p, size_bytes=p.stat().st_size))
        logger.info(f"Inbox scanned: {len(items)} files")
        return items
