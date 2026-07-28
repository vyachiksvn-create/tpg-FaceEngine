"""Unknown person workflow: review, candidate grouping, and identity promotion."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger

from feature.recognition.engine import RecognitionEngine
from feature.recognition.pipeline import RecognitionPipeline
from feature.search.index import FaissIndex
from feature.storage.database import get_session
from feature.storage.models import Identity, Photo


class UnknownStatus(str):
    UNKNOWN = "unknown"
    CANDIDATE = "candidate"
    REVIEW = "review"
    PROMOTED = "promoted"


@dataclass
class UnknownPhotoRecord:
    original_path: Path
    system_filename: str
    unknown_id: str
    status: str
    detected_at: datetime
    identity_id: int | None = None
    distance: float | None = None
    notes: str | None = None


@dataclass
class UnknownCandidateGroup:
    unknown_id: str
    status: str
    photo_count: int = 0
    avg_distance: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    promoted_identity_id: int | None = None
    photos: list[UnknownPhotoRecord] = field(default_factory=list)


class UnknownWorkflow:
    def __init__(self, review_root: Path, engine: RecognitionEngine, faiss: FaissIndex) -> None:
        self.review_root = Path(review_root)
        self.engine = engine
        self.faiss = faiss
        self._unknown_counter = 0
        self._groups: dict[str, UnknownCandidateGroup] = {}

    def process_unknown(self, photo_path: Path, search_results: list[tuple[int, float]]) -> UnknownPhotoRecord:
        self._unknown_counter += 1
        unknown_id = f"UNKNOWN_{self._unknown_counter:06d}"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        system_filename = f"{timestamp}_{unknown_id}{photo_path.suffix.lower()}"
        distance = search_results[0][1] if search_results else None

        record = UnknownPhotoRecord(
            original_path=photo_path,
            system_filename=system_filename,
            unknown_id=unknown_id,
            status=UnknownStatus.UNKNOWN,
            detected_at=datetime.utcnow(),
            distance=distance,
        )

        group = self._groups.get(unknown_id)
        if group is None:
            group = UnknownCandidateGroup(unknown_id=unknown_id, status=UnknownStatus.CANDIDATE)
            self._groups[unknown_id] = group
        group.photos.append(record)
        group.photo_count += 1
        if distance is not None:
            group.avg_distance = (group.avg_distance * (group.photo_count - 1) + distance) / group.photo_count
        return record

    def group_candidates(self, threshold: float = 0.25) -> list[UnknownCandidateGroup]:
        groups: dict[str, UnknownCandidateGroup] = {}
        for record in self._iter_records():
            matched_group = None
            for group in groups.values():
                if group.photos and self._distance(record, group.photos[0]) <= threshold:
                    matched_group = group
                    break
            if matched_group is None:
                unknown_id = record.unknown_id
                matched_group = UnknownCandidateGroup(unknown_id=unknown_id, status=UnknownStatus.CANDIDATE)
                groups[unknown_id] = matched_group
            matched_group.photos.append(record)
            matched_group.photo_count += 1
            if record.distance is not None:
                matched_group.avg_distance = (matched_group.avg_distance * (matched_group.photo_count - 1) + record.distance) / matched_group.photo_count
        self._groups = groups
        return list(groups.values())

    def promote_to_identity(self, unknown_id: str, display_name: str | None = None) -> Identity | None:
        group = self._groups.get(unknown_id)
        if not group:
            logger.warning(f"Candidate group not found: {unknown_id}")
            return None
        try:
            with get_session() as session:
                identity = Identity(
                    display_name=display_name or f"Unknown_{unknown_id}",
                    original_folder_name=unknown_id,
                    metadata_json="{}",
                )
                session.add(identity)
                session.flush()
                for record in group.photos:
                    photo = Photo(
                        identity_id=identity.id,
                        file_path=str(record.original_path),
                        sha256="",
                        width=0,
                        height=0,
                        thumbnail_path=None,
                        is_primary=False,
                    )
                    session.add(photo)
                    session.flush()
                group.promoted_identity_id = identity.id
                group.status = UnknownStatus.PROMOTED
                session.commit()
                logger.info(f"Promoted {unknown_id} to identity {identity.id}")
                return identity
        except Exception as exc:
            logger.error(f"Failed to promote {unknown_id}: {exc}")
            return None

    def get_groups(self) -> list[UnknownCandidateGroup]:
        return list(self._groups.values())

    def _iter_records(self) -> list[UnknownPhotoRecord]:
        records: list[UnknownPhotoRecord] = []
        for group in self._groups.values():
            records.extend(group.photos)
        return records

    @staticmethod
    def _distance(a: UnknownPhotoRecord, b: UnknownPhotoRecord) -> float:
        if a.distance is not None and b.distance is not None:
            return abs(a.distance - b.distance)
        return float("inf")
