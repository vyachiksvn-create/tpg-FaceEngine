"""Desktop: Identity Card panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus


class IdentityCard:
    def __init__(self, event_bus: "EventBus") -> None:
        self.event_bus = event_bus
        self._identity_id: int | None = None

    def show_identity(self, identity_id: int, name: str, photo_count: int, last_updated: str) -> None:
        self._identity_id = identity_id
        print(f"[IdentityCard] {name} | {photo_count} photos | updated {last_updated}")

    def clear(self) -> None:
        self._identity_id = None
        print("[IdentityCard] cleared")