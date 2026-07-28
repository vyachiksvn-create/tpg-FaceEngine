from __future__ import annotations

import json
import shutil
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from feature.core.events import EventPriority


@dataclass
class BackupManifest:
    created_at: float
    workspace: str
    files: list[str]
    metadata: dict[str, Any]


class BackupManager:
    def __init__(self, workspace_path: str | Path, event_bus: Any | None = None) -> None:
        self._workspace = Path(workspace_path)
        self._backup_dir = self._workspace / "Backup"
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._event_bus = event_bus
        self._max_backups = 7

    def subscribe(self) -> str | None:
        if not self._event_bus:
            return None
        return self._event_bus.subscribe(self._on_event, priority=EventPriority.HIGH)

    def create_backup(self, name: str | None = None) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_path = self._backup_dir / f"{backup_name}.zip"
        manifest = BackupManifest(
            created_at=time.time(),
            workspace=str(self._workspace),
            files=[],
            metadata={},
        )
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in sorted(self._workspace.rglob("*")):
                if item.is_file():
                    if any(part in item.parts for part in ["Backup", "Temp", ".git"]):
                        continue
                    arcname = item.relative_to(self._workspace)
                    zf.write(item, arcname)
                    manifest.files.append(str(arcname))
            manifest_json = json.dumps(manifest.__dict__, ensure_ascii=False, indent=2)
            zf.writestr("backup_manifest.json", manifest_json)
        self._cleanup_old_backups()
        logger.info(f"Backup created: {backup_path}")
        return backup_path

    def _on_event(self, event: Any) -> None:
        event_type = getattr(event, "event_type", "")
        if event_type in {"import.finished", "identity.merged", "profile.changed"}:
            self.create_backup(f"auto_{event_type.replace('.', '_')}")

    def _cleanup_old_backups(self) -> None:
        backups = sorted(self._backup_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in backups[self._max_backups :]:
            old.unlink(missing_ok=True)
            logger.info(f"Old backup removed: {old}")