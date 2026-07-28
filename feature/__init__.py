"""FaceArchive - Платформа для распознавания лиц"""

__version__ = "0.1.0-alpha"
__author__ = "FaceArchive Team"

from feature.config import ConfigManager, AppConfig
from feature.database.database import DatabaseManager
from feature.database.logger import setup_logger, get_logger
from feature.core import (
    EventBus,
    WorkspaceManager,
    ProfileManager,
    PluginManager,
    HistoryManager,
    DecisionEngine,
)

__all__ = [
    "__version__",
    "ConfigManager",
    "AppConfig",
    "DatabaseManager",
    "setup_logger",
    "get_logger",
    "EventBus",
    "WorkspaceManager",
    "ProfileManager",
    "PluginManager",
    "HistoryManager",
    "DecisionEngine",
]