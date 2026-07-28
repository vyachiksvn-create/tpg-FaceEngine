"""Desktop: Settings Panel"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus, ProfileManager


class SettingsPanel:
    def __init__(self, event_bus: "EventBus", profile_mgr: "ProfileManager") -> None:
        self.event_bus = event_bus
        self.profile_mgr = profile_mgr

    def show(self) -> None:
        pass

    def apply(self, profile_name: str) -> None:
        self.profile_mgr.activate(profile_name)