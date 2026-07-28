"""Gold dataset management for calibration and expert validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from feature.storage.models import Identity, Photo


@dataclass
class GoldSample:
    photo_path: Path
    correct_identity_id: int | None
    correct_display_name: str | None = None
    notes: str | None = None


@dataclass
class GoldDataset:
    samples: list[GoldSample] = field(default_factory=list)
    name: str = "default"

    def add(self, photo_path: Path, correct_identity_id: int | None, correct_display_name: str | None = None, notes: str | None = None) -> None:
        self.samples.append(GoldSample(
            photo_path=photo_path,
            correct_identity_id=correct_identity_id,
            correct_display_name=correct_display_name,
            notes=notes,
        ))

    def __len__(self) -> int:
        return len(self.samples)

    def save(self, path: Path) -> None:
        import json
        data = {
            "name": self.name,
            "samples": [
                {
                    "photo_path": str(s.photo_path),
                    "correct_identity_id": s.correct_identity_id,
                    "correct_display_name": s.correct_display_name,
                    "notes": s.notes,
                }
                for s in self.samples
            ],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> GoldDataset:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        dataset = cls(name=data.get("name", "default"))
        for s in data.get("samples", []):
            dataset.add(
                photo_path=Path(s["photo_path"]),
                correct_identity_id=s.get("correct_identity_id"),
                correct_display_name=s.get("correct_display_name"),
                notes=s.get("notes"),
            )
        return dataset
