"""Desktop: Confirm Workflow panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus


class ConfirmWorkflow:
    def __init__(self, event_bus: "EventBus") -> None:
        self.event_bus = event_bus

    def show(self, candidates_count: int) -> None:
        print(f"[ConfirmWorkflow] {candidates_count} candidates")

    def confirm(self, identity_id: int | None) -> None:
        print(f"[ConfirmWorkflow] Confirm: {identity_id}")

    def new_person(self) -> None:
        print("[ConfirmWorkflow] New person")

    def skip(self) -> None:
        print("[ConfirmWorkflow] Skip")

    def delete_photo(self) -> None:
        print("[ConfirmWorkflow] Delete photo")