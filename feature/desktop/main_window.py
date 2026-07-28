"""Desktop: Main Application Window"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from feature.core import EventBus, ProfileManager, WorkspaceManager


class MainWindow:
    def __init__(
        self,
        workspace_mgr: "WorkspaceManager",
        profile_mgr: "ProfileManager",
        event_bus: "EventBus",
    ) -> None:
        self.workspace_mgr = workspace_mgr
        self.profile_mgr = profile_mgr
        self.event_bus = event_bus
        logger.info("MainWindow initialized")

    def show(self) -> None:
        logger.info("MainWindow shown")

    def close(self) -> None:
        logger.info("MainWindow closed")