"""Feature: Desktop (operator workplace)"""

from feature.desktop.main_window import MainWindow
from feature.desktop.panels import (
    CandidatePanel,
    HistoryPanel,
    PhotoViewer,
    ProfilePanel,
    SettingsPanel,
    StatusBar,
    WorkspacePanel,
)
from feature.desktop.queue import QueueModel

__all__ = [
    "MainWindow",
    "QueueModel",
    "CandidatePanel",
    "HistoryPanel",
    "PhotoViewer",
    "ProfilePanel",
    "SettingsPanel",
    "StatusBar",
    "WorkspacePanel",
]