"""Desktop: Candidate Card model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CandidateCard:
    photo_id: int
    identity_id: int | None
    score: float
    distance: float
    face_size: int | None = None
    blur_score: float | None = None
    thumbnail_path: str | None = None
    identity_name: str = ""
    photo_count: int = 0