"""Feature: Desktop (operator workplace)"""

from feature.desktop.focus_mode import FocusMode, FocusModeController, FocusState
from feature.desktop.main_window import MainWindow
from feature.desktop.panels import (
    CandidateCard,
    CandidatePanel,
    ConfirmWorkflow,
    HistoryPanel,
    IdentityCard,
    PhotoViewer,
    ProfilePanel,
    SettingsPanel,
    StatusBar,
    WorkspacePanel,
)
from feature.desktop.queue import QueueModel
from feature.desktop.session import RecognitionSession, SessionStats

__all__ = [
    "FocusMode",
    "FocusModeController",
    "FocusState",
    "MainWindow",
    "QueueModel",
    "CandidateCard",
    "CandidatePanel",
    "ConfirmWorkflow",
    "HistoryPanel",
    "IdentityCard",
    "PhotoViewer",
    "ProfilePanel",
    "SettingsPanel",
    "StatusBar",
    "WorkspacePanel",
    "RecognitionSession",
    "SessionStats",
]