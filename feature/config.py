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
class ProfileConfig:
    name: str = "По умолчанию"
    description: str = ""
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    import_: ImportConfig = field(default_factory=ImportConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)


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
    profiles: dict[str, ProfileConfig] = field(default_factory=dict)
    active_profile: str = "default"
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)

    @property
    def active(self) -> ProfileConfig:
        if self.active_profile not in self.profiles:
            logger.warning(
                f"Профиль '{self.active_profile}' не найден, используется 'default'"
            )
            self.active_profile = "default"
        return self.profiles[self.active_profile]


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
            logger.info("Создается конфигурация по умолчанию")
            return self._default_config()

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
        profiles = {}
        for name, profile_data in raw.get("profiles", {}).items():
            profiles[name] = self._parse_profile(profile_data)

        return AppConfig(
            version=raw.get("version", "1.0"),
            paths=self._parse_paths(raw.get("paths", {})),
            profiles=profiles,
            active_profile=raw.get("active_profile", "default"),
            plugins=self._parse_plugins(raw.get("plugins", {})),
            logging=self._parse_logging(raw.get("logging", {})),
            database=self._parse_database(raw.get("database", {})),
            backup=self._parse_backup(raw.get("backup", {})),
        )

    def _parse_profile(self, data: dict[str, Any]) -> ProfileConfig:
        return ProfileConfig(
            name=data.get("name", "Профиль"),
            description=data.get("description", ""),
            recognition=RecognitionConfig(**data.get("recognition", {})),
            search=SearchConfig(**data.get("search", {})),
            import_=ImportConfig(**data.get("import", {})),
            quality=QualityConfig(**data.get("quality", {})),
            gui=GUIConfig(**data.get("gui", {})),
            performance=PerformanceConfig(**data.get("performance", {})),
        )

    def _parse_paths(self, data: dict[str, Any]) -> PathsConfig:
        return PathsConfig(**data)

    def _parse_plugins(self, data: dict[str, Any]) -> PluginsConfig:
        return PluginsConfig(
            recognition=data.get("recognition", ["insightface"]),
            search=data.get("search", ["faiss"]),
            import_=data.get("import", ["basic"]),
        )

    def _parse_logging(self, data: dict[str, Any]) -> LoggingConfig:
        return LoggingConfig(**data)

    def _parse_database(self, data: dict[str, Any]) -> DatabaseConfig:
        return DatabaseConfig(**data)

    def _parse_backup(self, data: dict[str, Any]) -> BackupConfig:
        return BackupConfig(**data)

    def _default_config(self) -> AppConfig:
        return AppConfig(
            profiles={
                "default": ProfileConfig(
                    name="По умолчанию",
                    description="Сбалансированные настройки",
                )
            },
            active_profile="default",
        )

    def save_config(self, config: AppConfig, path: str | Path | None = None) -> None:
        target = Path(path) if path else self._find_config()
        target.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": config.version,
            "paths": self._dataclass_to_dict(config.paths),
            "active_profile": config.active_profile,
            "profiles": {
                name: self._dataclass_to_dict(profile)
                for name, profile in config.profiles.items()
            },
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
                if isinstance(value, list):
                    result[key] = value
                elif hasattr(value, "__dataclass_fields__"):
                    result[key] = self._dataclass_to_dict(value)
                else:
                    result[key] = value
            return result
        return obj

    def create_workspace(self, paths: PathsConfig) -> None:
        dirs = [
            paths.workspace,
            os.path.join(paths.workspace, "storage"),
            paths.incoming,
            paths.rejected,
            paths.export,
            paths.logs,
            paths.backup,
            paths.temp,
            paths.thumbnails,
        ]
        for d in dirs:
            if d:
                Path(d).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Создан каталог: {d}")

    @property
    def config(self) -> AppConfig:
        return self._config
