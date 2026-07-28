"""Desktop: Layout Manager."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class PanelLayout:
    name: str
    panels: dict[str, dict[str, Any]] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class LayoutManager:
    def __init__(self, layouts_dir: str | Path | None = None) -> None:
        self._layouts_dir = Path(layouts_dir) if layouts_dir else Path.cwd() / "layouts"
        self._layouts_dir.mkdir(parents=True, exist_ok=True)
        self._current: str = "default"

    def save(self, layout: PanelLayout) -> Path:
        path = self._layouts_dir / f"{layout.name}.layout.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(layout.__dict__, f, indent=2, ensure_ascii=False)
        logger.info(f"Layout saved: {path}")
        return path

    def load(self, name: str) -> PanelLayout:
        path = self._layouts_dir / f"{name}.layout.json"
        if not path.exists():
            raise FileNotFoundError(f"Layout '{name}' not found")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return PanelLayout(**data)

    def list_layouts(self) -> list[str]:
        return [p.stem.replace(".layout", "") for p in self._layouts_dir.glob("*.layout.json")]

    def set_current(self, name: str) -> None:
        self._current = name

    @property
    def current(self) -> str:
        return self._current