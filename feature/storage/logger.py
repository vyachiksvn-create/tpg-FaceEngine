from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger

from feature.config import ConfigManager


def setup_logger(config: Any = None) -> None:
    if config is None:
        config = ConfigManager.get_instance()

    log_config = config.logging
    log_path = Path(config.paths.logs) / "facearchive.log"

    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_config.level,
        colorize=True,
    )

    logger.add(
        str(log_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=log_config.level,
        rotation=log_config.rotation,
        retention=log_config.retention,
        encoding=log_config.encoding,
        compression="zip",
    )

    logger.info("Логгер инициализирован")
    logger.info(f"Уровень логирования: {log_config.level}")
    logger.info(f"Файл логов: {log_path}")


def get_logger(name: str) -> Any:
    return logger.bind(name=name)