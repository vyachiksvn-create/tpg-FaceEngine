"""FaceArchive - Платформа для распознавания лиц"""

__version__ = "0.1.0-alpha"
__author__ = "FaceArchive Team"

from feature.config import ConfigManager, AppConfig
from feature.database.database import DatabaseManager
from feature.database.logger import setup_logger, get_logger

__all__ = [
    "__version__",
    "ConfigManager",
    "AppConfig",
    "DatabaseManager",
    "setup_logger",
    "get_logger",
]
