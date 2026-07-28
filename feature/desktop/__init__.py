"""Feature: Desktop (operator workplace)"""

from feature.desktop.main_window import MainWindow
from feature.desktop.panels import (
    CandidatePanel,
    HistoryPanel,
    ProfilePanel,
    SettingsPanel,
    WorkspacePanel,
)

__all__ = [
    "MainWindow",
    "CandidatePanel",
    "HistoryPanel",
    "ProfilePanel",
    "SettingsPanel",
    "WorkspacePanel",
]