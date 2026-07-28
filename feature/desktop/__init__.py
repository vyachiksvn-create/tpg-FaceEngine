"""Feature: Desktop (operator workplace)"""

from feature.desktop.focus_mode import FocusMode, FocusModeController, FocusState
from feature.desktop.layout_manager import LayoutManager, PanelLayout
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
from feature.desktop.shortcut_manager import Shortcut, ShortcutManager
from feature.desktop.theme_manager import Theme, ThemeConfig, ThemeManager

__all__ = [
    "FocusMode",
    "FocusModeController",
    "FocusState",
    "LayoutManager",
    "PanelLayout",
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
    "Shortcut",
    "ShortcutManager",
    "Theme",
    "ThemeConfig",
    "ThemeManager",
]