from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger


@dataclass
class PathsConfig:
    workspace: str = ""
    base_photos: str = ""
    incoming: str = ""
    rejected: str = ""
    export: str = ""
    logs: str = ""
    backup: str = ""
    temp: str = ""
    thumbnails: str = ""
    review: str = ""
    matches: str = ""
    reports: str = ""


@dataclass
class RecognitionConfig:
    engine: str = "insightface"
    model: str = "buffalo_l"
    threshold: float = 0.6
    max_faces_per_image: int = 5
    use_gpu: bool = False


@dataclass
class SearchConfig:
    index_type: str = "flat"
    top_k: int = 10
    merge_strategy: str = "hybrid"


@dataclass
class ImportConfig:
    check_duplicates: bool = True
    compute_sha256: bool = True
    save_thumbnails: bool = True
    auto_rotate: bool = True
    auto_contrast: bool = False
    quality_check: bool = True


@dataclass
class QualityConfig:
    min_face_size: int = 80
    max_blur_threshold: float = 100.0
    max_yaw_angle: float = 30.0
    max_pitch_angle: float = 20.0
    min_confidence: float = 0.5


@dataclass
class GUIConfig:
    theme: str = "system"
    view_mode: str = "cards"
    thumbnail_size: int = 256
    language: str = "ru"


@dataclass
class PerformanceConfig:
    import_threads: int = 4
    cache_size: int = 1000
    auto_build_index: bool = True


@dataclass
class DatabaseConfig:
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class LoggingConfig:
    level: str = "INFO"
    rotation: str = "10 MB"
    retention: str = "30 days"
    encoding: str = "utf-8"


@dataclass
class BackupConfig:
    auto_backup: bool = True
    interval_hours: int = 24
    keep_last: int = 7


@dataclass
class PluginsConfig:
    recognition: list[str] = field(default_factory=lambda: ["insightface"])
    search: list[str] = field(default_factory=lambda: ["faiss"])
    import_: list[str] = field(default_factory=lambda: ["basic"])


@dataclass
class AppConfig:
    version: str = "1.0"
    paths: PathsConfig = field(default_factory=PathsConfig)
    active_profile: str = "default"
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)


class ConfigManager:
    _instance: AppConfig | None = None
    _config_path: Path | None = None

    def __init__(self, config_path: str | Path | None = None) -> None:
        if ConfigManager._instance is not None:
            raise RuntimeError("ConfigManager уже инициализирован. Используйте get_instance()")
        self._config_path = Path(config_path) if config_path else None
        self._config = self._load_config()

    @classmethod
    def get_instance(cls, config_path: str | Path | None = None) -> AppConfig:
        if cls._instance is None:
            cls._instance = cls(config_path)._config
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls._config_path = None

    def _load_config(self) -> AppConfig:
        config_path = self._find_config()
        if not config_path.exists():
            logger.warning(f"Конфигурационный файл не найден: {config_path}")
            return AppConfig()

        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        return self._parse_config(raw)

    def _find_config(self) -> Path:
        if self._config_path:
            return self._config_path
        candidates = [
            Path.cwd() / "config.yaml",
            Path.cwd() / "config.yml",
            Path(__file__).parent.parent.parent / "config.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return Path.cwd() / "config.yaml"

    def _parse_config(self, raw: dict[str, Any]) -> AppConfig:
        return AppConfig(
            version=raw.get("version", "1.0"),
            paths=self._parse_paths(raw.get("paths", {})),
            active_profile=raw.get("active_profile", "default"),
            recognition=self._parse_recognition(raw.get("recognition", {})),
            plugins=self._parse_plugins(raw.get("plugins", {})),
            logging=self._parse_logging(raw.get("logging", {})),
            database=self._parse_database(raw.get("database", {})),
            backup=self._parse_backup(raw.get("backup", {})),
        )

    def _parse_profile(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": data.get("name", "Профиль"),
            "description": data.get("description", ""),
            "recognition": data.get("recognition", {}),
            "search": data.get("search", {}),
            "import": data.get("import", {}),
            "quality": data.get("quality", {}),
            "gui": data.get("gui", {}),
            "performance": data.get("performance", {}),
        }

    def _parse_paths(self, data: dict[str, Any]) -> PathsConfig:
        return PathsConfig(**data)

    def _parse_plugins(self, data: dict[str, Any]) -> PluginsConfig:
        return PluginsConfig(
            recognition=data.get("recognition", ["insightface"]),
            search=data.get("search", ["faiss"]),
            import_=data.get("import", ["basic"]),
        )

    def _parse_recognition(self, data: dict[str, Any]) -> RecognitionConfig:
        return RecognitionConfig(**data)

    def _parse_logging(self, data: dict[str, Any]) -> LoggingConfig:
        return LoggingConfig(**data)

    def _parse_database(self, data: dict[str, Any]) -> DatabaseConfig:
        return DatabaseConfig(**data)

    def _parse_backup(self, data: dict[str, Any]) -> BackupConfig:
        return BackupConfig(**data)

    def save_config(self, config: AppConfig, path: str | Path | None = None) -> None:
        target = Path(path) if path else self._find_config()
        target.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": config.version,
            "paths": self._dataclass_to_dict(config.paths),
            "active_profile": config.active_profile,
            "recognition": self._dataclass_to_dict(config.recognition),
            "plugins": self._dataclass_to_dict(config.plugins),
            "logging": self._dataclass_to_dict(config.logging),
            "database": self._dataclass_to_dict(config.database),
            "backup": self._dataclass_to_dict(config.backup),
        }
        with open(target, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        logger.info(f"Конфигурация сохранена: {target}")

    def _dataclass_to_dict(self, obj: Any) -> dict[str, Any]:
        if hasattr(obj, "__dataclass_fields__"):
            result = {}
            for key, value in obj.__dict__.items():
                if key.startswith("_"):
                    continue
                result[key] = value
            return result
        return obj

    def create_workspace(self, paths: PathsConfig) -> None:
        dirs = [
            paths.workspace,
            os.path.join(paths.workspace, "storage"),
            paths.base_photos,
            paths.incoming,
            os.path.join(paths.rejected, "NoFace"),
            os.path.join(paths.rejected, "BadQuality"),
            os.path.join(paths.rejected, "Errors"),
            paths.review,
            os.path.join(paths.review, "Unknown"),
            os.path.join(paths.review, "NeedConfirm"),
            os.path.join(paths.review, "NewPersons"),
            paths.matches,
            paths.export,
            os.path.join(paths.workspace, "database"),
            os.path.join(paths.workspace, "faiss"),
            os.path.join(paths.workspace, "cache"),
            paths.logs,
            paths.backup,
            paths.temp,
            paths.thumbnails,
            paths.reports,
        ]
        for d in dirs:
            if d:
                Path(d).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Создан каталог: {d}")

    @property
    def config(self) -> AppConfig:
        return self._config