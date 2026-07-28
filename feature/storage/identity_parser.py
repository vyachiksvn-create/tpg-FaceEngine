"""Identity parsing and metadata helpers."""

from __future__ import annotations

import json
import re
from typing import Any


class IdentityParser:
    DEFAULT_SEPARATOR = " - "

    @classmethod
    def parse_folder_name(cls, folder_name: str) -> tuple[str, dict[str, Any]]:
        display_name = folder_name.strip()
        metadata: dict[str, Any] = {}
        if cls.DEFAULT_SEPARATOR in folder_name:
            parts = folder_name.split(cls.DEFAULT_SEPARATOR, 1)
            display_name = parts[0].strip()
            metadata["legacy_label"] = parts[1].strip()
        return display_name, metadata

    @classmethod
    def build_metadata_json(cls, extra: dict[str, Any] | None = None) -> str | None:
        payload: dict[str, Any] = {}
        if extra:
            payload.update(extra)
        if not payload:
            return None
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    @classmethod
    def load_metadata_json(cls, data: str | None) -> dict[str, Any]:
        if not data:
            return {}
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}