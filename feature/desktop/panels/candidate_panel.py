"""Desktop: Candidate Panel with cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus
    from feature.desktop.panels.candidate_card import CandidateCard


class CandidatePanel:
    def __init__(self, event_bus: "EventBus") -> None:
        self.event_bus = event_bus
        self._cards: list[CandidateCard] = []

    def show_candidates(self, cards: list["CandidateCard"]) -> None:
        self._cards = cards
        for card in cards:
            print(f"[Candidate] {card.score:.1%} - {card.identity_name} ({card.photo_count} photos)")

    def confirm(self, identity_id: int | None) -> None:
        print(f"[Candidate] Confirm identity: {identity_id}")

    def reject(self) -> None:
        print("[Candidate] Reject")