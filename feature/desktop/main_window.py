"""Desktop MVP: Main Window."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

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
        self._window: QMainWindow | None = None
        logger.info("MainWindow initialized")

    def show(self) -> None:
        logger.info("MainWindow shown")

    def close(self) -> None:
        logger.info("MainWindow closed")