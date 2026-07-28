from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger


class WorkspaceStatus(str, Enum):
    READY = "ready"
    INITIALIZING = "initializing"
    ERROR = "error"
    LOCKED = "locked"


@dataclass
class WorkspacePaths:
    root: str = ""
    database: str = ""
    storage: str = ""
    thumbnails: str = ""
    logs: str = ""
    backup: str = ""
    temp: str = ""
    export: str = ""
    rejected: str = ""

    def create_directories(self) -> None:
        dirs = [
            self.root,
            self.storage,
            self.thumbnails,
            self.logs,
            self.backup,
            self.temp,
            self.export,
            self.rejected,
        ]
        for d in dirs:
            if d:
                Path(d).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Workspace directory created: {d}")


@dataclass
class Workspace:
    name: str
    path: str
    status: WorkspaceStatus = WorkspaceStatus.READY
    paths: WorkspacePaths = field(default_factory=WorkspacePaths)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_active: bool = False

    def __post_init__(self) -> None:
        if not self.paths.root:
            self.paths = WorkspacePaths(
                root=str(Path(self.path)),
                database=str(Path(self.path) / "storage" / "faces.db"),
                storage=str(Path(self.path) / "storage"),
                thumbnails=str(Path(self.path) / "Thumbnails"),
                logs=str(Path(self.path) / "Logs"),
                backup=str(Path(self.path) / "Backup"),
                temp=str(Path(self.path) / "Temp"),
                export=str(Path(self.path) / "Export"),
                rejected=str(Path(self.path) / "Rejected"),
            )


class WorkspaceManager:
    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._base_dir = Path(base_dir) if base_dir else Path.cwd() / "Workspaces"
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._workspaces: dict[str, Workspace] = {}
        self._active: str | None = None

    def create(self, name: str, path: str | None = None) -> Workspace:
        if name in self._workspaces:
            raise ValueError(f"Workspace '{name}' already exists")

        workspace_path = Path(path) if path else self._base_dir / name
        workspace_path.mkdir(parents=True, exist_ok=True)

        workspace = Workspace(name=name, path=str(workspace_path))
        workspace.paths.create_directories()
        workspace.metadata = {
            "created_at": time.time(),
            "version": "0.1.0-alpha",
        }

        self._workspaces[name] = workspace
        self._save_registry()
        logger.info(f"Workspace created: {name} at {workspace_path}")
        return workspace

    def load(self, name: str) -> Workspace:
        if name not in self._workspaces:
            raise ValueError(f"Workspace '{name}' not found")
        return self._workspaces[name]

    def activate(self, name: str) -> Workspace:
        if name not in self._workspaces:
            raise ValueError(f"Workspace '{name}' not found")
        if self._active:
            self._workspaces[self._active].is_active = False
        self._active = name
        self._workspaces[name].is_active = True
        self._save_registry()
        logger.info(f"Workspace activated: {name}")
        return self._workspaces[name]

    def delete(self, name: str) -> None:
        if name not in self._workspaces:
            raise ValueError(f"Workspace '{name}' not found")
        if self._active == name:
            raise RuntimeError("Cannot delete active workspace")
        ws = self._workspaces.pop(name)
        import shutil
        shutil.rmtree(ws.path, ignore_errors=True)
        self._save_registry()
        logger.info(f"Workspace deleted: {name}")

    def list_workspaces(self) -> list[Workspace]:
        return list(self._workspaces.values())

    @property
    def active(self) -> Workspace | None:
        if self._active and self._active in self._workspaces:
            return self._workspaces[self._active]
        return None

    def _save_registry(self) -> None:
        registry_path = self._base_dir / "workspaces.json"
        data = {
            "active": self._active,
            "workspaces": {
                name: {
                    "name": ws.name,
                    "path": ws.path,
                    "status": ws.status.value,
                    "metadata": ws.metadata,
                }
                for name, ws in self._workspaces.items()
            },
        }
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_registry(self) -> None:
        registry_path = self._base_dir / "workspaces.json"
        if not registry_path.exists():
            return
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, ws_data in data.get("workspaces", {}).items():
                ws = Workspace(
                    name=ws_data["name"],
                    path=ws_data["path"],
                    status=WorkspaceStatus(ws_data.get("status", "ready")),
                    metadata=ws_data.get("metadata", {}),
                )
                self._workspaces[name] = ws
            self._active = data.get("active")
            if self._active and self._active in self._workspaces:
                self._workspaces[self._active].is_active = True
        except Exception as exc:
            logger.error(f"Failed to load workspace registry: {exc}")