"""Desktop: Candidate Panel"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus


class CandidatePanel:
    def __init__(self, event_bus: "EventBus") -> None:
        self.event_bus = event_bus

    def show_candidates(self, candidates: list[dict]) -> None:
        pass

    def confirm(self, identity_id: int | None) -> None:
        pass

    def reject(self) -> None:
        pass