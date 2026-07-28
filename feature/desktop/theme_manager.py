"""Desktop: Theme Manager."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Theme(str, Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


@dataclass
class ThemeConfig:
    name: str = "system"
    primary_color: str = "#0078d4"
    background: str = "#ffffff"
    surface: str = "#f3f3f3"
    text: str = "#000000"
    border: str = "#e5e5e5"


class ThemeManager:
    def __init__(self) -> None:
        self._current = Theme.SYSTEM
        self._config = ThemeConfig()

    def set_theme(self, theme: Theme) -> None:
        self._current = theme

    def get_theme(self) -> Theme:
        return self._current

    def get_colors(self) -> ThemeConfig:
        return self._config