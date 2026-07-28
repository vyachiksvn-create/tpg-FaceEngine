"""Desktop: Photo Viewer."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class PhotoViewer:
    def __init__(self, parent: QWidget | None = None) -> None:
        self._parent = parent

    def load(self, path: str) -> None:
        pass

    def clear(self) -> None:
        pass

    def set_face_box(self, bbox: tuple[int, int, int, int]) -> None:
        pass