"""Unified image loader with Unicode-safe fallbacks."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from loguru import logger

from feature.storage.models import QualityCheck


class ImageLoadError(Exception):
    def __init__(self, reason: str, path: Path) -> None:
        super().__init__(reason)
        self.reason = reason
        self.path = path


class ImageLoader:
    @staticmethod
    def load(path: Path) -> np.ndarray:
        if not path.exists():
            raise ImageLoadError("missing_file", path)
        if path.stat().st_size == 0:
            raise ImageLoadError("empty_file", path)

        try:
            data = np.fromfile(str(path), dtype=np.uint8)
            if data.size == 0:
                raise ImageLoadError("empty_bytes", path)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if image is not None:
                return image
        except Exception as exc:
            logger.debug(f"np.fromfile loader failed for {path}: {exc}")

        try:
            from PIL import Image
            with Image.open(path) as img:
                img = img.convert("RGB")
                return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as exc:
            logger.debug(f"PIL fallback failed for {path}: {exc}")

        raise ImageLoadError("decode_failed", path)

    @staticmethod
    def try_load(path: Path) -> tuple[np.ndarray | None, str | None]:
        try:
            return ImageLoader.load(path), None
        except ImageLoadError as error:
            return None, error.reason
        except Exception as exc:
            return None, f"unexpected:{exc}"
