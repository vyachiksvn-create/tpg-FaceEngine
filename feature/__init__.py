"""FaceArchive - Платформа для распознавания лиц"""

__version__ = "0.1.0-alpha"
__author__ = "FaceArchive Team"

from feature.config import ConfigManager, AppConfig
from feature.storage.database import DatabaseManager
from feature.storage.logger import setup_logger, get_logger
from feature.core import (
    DOMAIN_EVENTS,
    IService,
    EventBus,
    WorkspaceManager,
    ProfileManager,
    PluginManager,
    HistoryManager,
    DecisionEngine,
    JobManager,
    BackupManager,
)

__all__ = [
    "__version__",
    "ConfigManager",
    "AppConfig",
    "DatabaseManager",
    "setup_logger",
    "get_logger",
    "DOMAIN_EVENTS",
    "IService",
    "EventBus",
    "WorkspaceManager",
    "ProfileManager",
    "PluginManager",
    "HistoryManager",
    "DecisionEngine",
    "JobManager",
    "BackupManager",
]