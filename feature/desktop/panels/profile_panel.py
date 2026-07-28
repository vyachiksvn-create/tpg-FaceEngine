"""Desktop: Profile Panel"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus, ProfileManager


class ProfilePanel:
    def __init__(self, event_bus: "EventBus", profile_mgr: "ProfileManager") -> None:
        self.event_bus = event_bus
        self.profile_mgr = profile_mgr

    def list_profiles(self) -> list[str]:
        return self.profile_mgr.list_profiles()

    def activate(self, name: str) -> None:
        self.profile_mgr.activate(name)