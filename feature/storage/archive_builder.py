"""Archive Builder: import Known base into Workspace."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np
from loguru import logger

from feature.core.events import Event, EventBus
from feature.import_.importer import PhotoImporter
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex
from feature.storage.database import DatabaseManager, get_session
from feature.storage.identity_parser import IdentityParser
from feature.storage.models import Embedding, Identity, ImportLog, ImportStatus, Photo, QualityCheck


@dataclass
class ArchiveBuildResult:
    total_persons: int = 0
    total_photos: int = 0
    imported: int = 0
    skipped: int = 0
    errors: int = 0
    elapsed_ms: float = 0.0
    faiss_vectors: int = 0


class ArchiveBuilder:
    def __init__(
        self,
        known_path: Path,
        workspace_path: Path,
        event_bus: EventBus | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
    ) -> None:
        self.known_path = Path(known_path)
        self.workspace_path = Path(workspace_path)
        self.event_bus = event_bus
        self.progress_callback = progress_callback
        self.result = ArchiveBuildResult()

    def run(self) -> ArchiveBuildResult:
        t0 = time.perf_counter()
        logger.info(f"ArchiveBuilder started: {self.known_path}")

        if not self.known_path.exists() or not self.known_path.is_dir():
            logger.error(f"Known path not found: {self.known_path}")
            return self.result

        person_dirs = [
            p for p in self.known_path.iterdir()
            if p.is_dir() and p.name.lower() != "x" and p.name.lower() != "unknown"
        ]
        self.result.total_persons = len(person_dirs)
        logger.info(f"Found {len(person_dirs)} person directories")

        db = DatabaseManager.get_instance()
        db.init_db(create_tables=True)

        recognition = RecognitionEngine()
        recognition.load_model()

        faiss = FaissIndex(dimension=512)
        faiss.create_index("flat")

        processed_photos = 0
        total_photos = self._count_photos(person_dirs)

        for idx, person_dir in enumerate(person_dirs):
            try:
                self._import_person(person_dir, recognition, faiss)
                processed = self._count_photos([person_dir])
                processed_photos += processed
                if self.progress_callback:
                    progress = processed_photos / total_photos if total_photos > 0 else 0.0
                    self.progress_callback(progress, f"Обработано персон: {idx + 1}/{len(person_dirs)}")
            except Exception as exc:
                logger.error(f"Failed to import person {person_dir.name}: {exc}")
                self.result.errors += 1

        self.result.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.result.faiss_vectors = faiss.total_vectors

        logger.info(
            f"ArchiveBuilder finished: persons={self.result.total_persons}, "
            f"photos={self.result.imported}, skipped={self.result.skipped}, "
            f"errors={self.result.errors}, time={self.result.elapsed_ms:.0f}ms"
        )
        return self.result

    def _import_person(self, person_dir: Path, recognition: RecognitionEngine, faiss: FaissIndex) -> None:
        display_name, extra_metadata = IdentityParser.parse_folder_name(person_dir.name)
        metadata_json = IdentityParser.build_metadata_json(extra_metadata)

        with get_session() as session:
            identity = Identity(
                display_name=display_name,
                original_folder_name=person_dir.name,
                metadata_json=metadata_json,
            )
            session.add(identity)
            session.flush()

            photo_files = [
                p for p in person_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
            ]

            for photo_path in photo_files:
                try:
                    sha256 = PhotoImporter.compute_sha256(photo_path)
                    existing_log = session.query(ImportLog).filter_by(sha256=sha256).first()
                    if existing_log and existing_log.status == ImportStatus.IMPORTED:
                        self.result.skipped += 1
                        continue

                    image = cv2.imread(str(photo_path))
                    if image is None:
                        logger.warning(f"Cannot read image: {photo_path}")
                        self.result.errors += 1
                        continue

                    faces = recognition.detect_faces(image)
                    if not faces:
                        logger.warning(f"No faces detected: {photo_path}")
                        self.result.errors += 1
                        continue

                    height, width = image.shape[:2]
                    thumbnail_path = None
                    try:
                        thumb_dir = self.workspace_path / "Thumbnails"
                        thumb_dir.mkdir(parents=True, exist_ok=True)
                        thumbnail_name = f"{sha256[:16]}.jpg"
                        thumbnail_path = thumb_dir / thumbnail_name
                        PhotoImporter.save_thumbnail(photo_path, thumbnail_path, 256)
                    except Exception:
                        pass

                    photo = Photo(
                        identity_id=identity.id,
                        file_path=str(photo_path),
                        sha256=sha256,
                        width=width,
                        height=height,
                        thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
                        is_primary=True,
                    )
                    session.add(photo)
                    session.flush()

                    primary_face = faces[0]
                    embedding_vector = recognition.get_embedding(image, primary_face)
                    embedding = Embedding(
                        photo_id=photo.id,
                        model_name="buffalo_l",
                    )
                    embedding.set_vector(embedding_vector)
                    session.add(embedding)
                    session.flush()

                    bbox = primary_face.bbox.astype(int)
                    quality_data = PhotoImporter.assess_quality(image, tuple(bbox))
                    qc = QualityCheck(
                        photo_id=photo.id,
                        blur_score=quality_data.get("blur_score"),
                        face_size=quality_data.get("face_size"),
                        yaw_angle=quality_data.get("yaw_angle"),
                        pitch_angle=quality_data.get("pitch_angle"),
                        confidence=quality_data.get("confidence"),
                        is_good_quality=quality_data.get("blur_score", 0) > 100.0,
                    )
                    session.add(qc)

                    log = ImportLog(
                        file_path=str(photo_path),
                        sha256=sha256,
                        status=ImportStatus.IMPORTED,
                        imported_at=datetime.utcnow(),
                        photo_id=photo.id,
                    )
                    session.add(log)

                    faiss.add_vectors(embedding_vector, [photo.id])
                    self.result.imported += 1

                except Exception as exc:
                    logger.error(f"Error importing {photo_path}: {exc}")
                    self.result.errors += 1

            session.commit()

    def _count_photos(self, directories: list[Path]) -> int:
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        return sum(
            1 for d in directories
            for p in d.rglob("*")
            if p.is_file() and p.suffix.lower() in exts
        )