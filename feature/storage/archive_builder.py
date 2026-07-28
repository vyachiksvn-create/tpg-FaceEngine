"""Archive Builder: import Known base into Workspace."""

from __future__ import annotations

import string
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
from loguru import logger

from feature.config import ConfigManager
from feature.core.events import Event, EventBus
from feature.import_.importer import compute_sha256, save_thumbnail
from feature.recognition.benchmark import BenchmarkManager
from feature.recognition.engine import RecognitionEngine
from feature.recognition.quality import QualityAnalyzer
from feature.search.index import FaissIndex
from feature.storage.archive_report import ArchiveReport
from feature.storage.database import DatabaseManager, get_session
from feature.storage.duplicate_detector import DuplicateDetector
from feature.storage.identity_parser import IdentityParser
from feature.storage.image_loader import ImageLoadError, ImageLoader
from feature.storage.models import Embedding, Identity, ImportLog, ImportStatus, Photo, QualityCheck
from feature.storage.reject_manager import RejectManager


@dataclass
class ArchiveBuildResult:
    total_persons: int = 0
    total_photos: int = 0
    imported: int = 0
    skipped: int = 0
    errors: int = 0
    elapsed_ms: float = 0.0
    faiss_vectors: int = 0
    report: ArchiveReport | None = None


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
        self.reject_manager = RejectManager()
        self.report = ArchiveReport()
        self.benchmark = BenchmarkManager()
        self.quality_analyzer = QualityAnalyzer()
        self.duplicate_detector = DuplicateDetector()
        self._embedding_times: list[float] = []
        self._person_counter = 0

    def run(self) -> ArchiveBuildResult:
        t0 = time.perf_counter()
        logger.info(f"ArchiveBuilder started: {self.known_path}")

        if not self.known_path.exists() or not self.known_path.is_dir():
            logger.error(f"Known path not found: {self.known_path}")
            self.result.report = self.report
            return self.result

        person_dirs = [
            p for p in self.known_path.rglob("*")
            if p.is_dir() and p.name.lower() not in {"x", "unknown"}
        ]
        if not person_dirs:
            person_dirs = [self.known_path]
        self.result.total_persons = len(person_dirs)
        self.report.persons_total = len(person_dirs)
        self.benchmark.build.persons_total = len(person_dirs)
        logger.info(f"Found {len(person_dirs)} person directories")

        db = DatabaseManager.get_instance()
        db.init_db(create_tables=True)

        config = ConfigManager.get_instance()
        recognition = RecognitionEngine(config)
        recognition.load_model()

        faiss = FaissIndex(dimension=512)
        faiss.create_index("flat")

        photo_files = [
            p
            for d in person_dirs
            for p in d.rglob("*")
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        self.result.total_photos = len(photo_files)
        self.report.photos_total = len(photo_files)
        self.benchmark.build.photos_total = len(photo_files)

        processed = 0
        for photo_path in photo_files:
            self._import_photo(photo_path, recognition, faiss)
            processed += 1
            if self.progress_callback:
                progress = processed / len(photo_files) if photo_files else 0.0
                self.progress_callback(progress, f"Обработано: {processed}/{len(photo_files)}")

        self._finalize_identities()

        self.result.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.result.faiss_vectors = faiss.total_vectors

        self.report.imported = self.result.imported
        self.report.rejected = self.reject_manager.stats.total_rejected
        self.report.rejection_reasons = self.reject_manager.summary()
        self.report.rejection_records = self.reject_manager.as_dict().get("records", [])
        if self._embedding_times:
            self.report.avg_embedding_ms = sum(self._embedding_times) / len(self._embedding_times)
            self.report.median_embedding_ms = float(np.median(self._embedding_times))
            self.report.max_embedding_ms = float(max(self._embedding_times))
        self.report.faiss_vectors = faiss.total_vectors
        self.report.build_time_s = self.result.elapsed_ms / 1000.0

        self.benchmark.build.build_time_s = self.report.build_time_s
        self.benchmark.build.embedding_count = len(self._embedding_times)
        if self._embedding_times:
            self.benchmark.build.avg_embedding_ms = sum(self._embedding_times) / len(self._embedding_times)
            self.benchmark.build.median_embedding_ms = float(np.median(self._embedding_times))
            self.benchmark.build.max_embedding_ms = float(max(self._embedding_times))
        self.benchmark.build.imported = self.result.imported
        self.benchmark.build.rejected = self.report.rejected
        self.benchmark.build.skipped = self.result.skipped
        self.benchmark.build.errors = self.result.errors

        try:
            with get_session() as session:
                self.report.sqlite_identities = session.query(Identity).count()
                self.report.sqlite_photos = session.query(Photo).count()
                self.report.sqlite_embeddings = session.query(Embedding).count()
        except Exception as exc:
            logger.warning(f"Cannot read SQLite stats: {exc}")

        self.result.report = self.report
        self.report.print()
        self.benchmark.print_report()

        logger.info(
            f"ArchiveBuilder finished: persons={self.result.total_persons}, "
            f"photos={self.result.imported}, rejected={self.report.rejected}, "
            f"errors={self.result.errors}, time={self.result.elapsed_ms:.0f}ms"
        )
        return self.result

    def _finalize_identities(self) -> None:
        try:
            with get_session() as session:
                identities = session.query(Identity).all()
                for identity in identities:
                    photos = session.query(Photo).filter_by(identity_id=identity.id).all()
                    if not photos:
                        continue
                    photo_embeddings = []
                    for photo in photos:
                        emb = session.query(Embedding).filter_by(photo_id=photo.id).first()
                        if emb is not None:
                            vec = emb.get_vector()
                            if vec is not None and vec.size > 0:
                                photo_embeddings.append((photo.id, vec))
                    if not photo_embeddings:
                        continue
                    duplicates = self.duplicate_detector.find_within_identity(photo_embeddings)
                    if duplicates:
                        logger.info(f"Found {len(duplicates)} duplicates for identity {identity.id}")
                    best_photo_id = photo_embeddings[0][0]
                    best_score = -1.0
                    for photo in photos:
                        if photo.quality_score is not None and photo.quality_score > best_score:
                            best_score = photo.quality_score
                            best_photo_id = photo.id
                    identity.representative_photo_id = best_photo_id
                    if photos:
                        avg_quality = sum(p.quality_score or 0.0 for p in photos) / len(photos)
                        identity.health_score = min(avg_quality, 100.0)
                session.commit()
        except Exception as exc:
            logger.warning(f"Cannot finalize identities: {exc}")

    def _import_photo(self, photo_path: Path, recognition: RecognitionEngine, faiss: FaissIndex) -> None:
        try:
            sha256 = compute_sha256(photo_path)
            with get_session() as session:
                existing_log = session.query(ImportLog).filter_by(sha256=sha256).first()
                if existing_log and existing_log.status == ImportStatus.IMPORTED:
                    self.result.skipped += 1
                    return

            image, load_reason = ImageLoader.try_load(photo_path)
            if image is None:
                self.reject_manager.record(photo_path, load_reason or "cannot_read")
                self._inject_rejection(load_reason)
                return

            faces = recognition.detect_faces(image)
            if not faces:
                self.reject_manager.record(photo_path, "no_face")
                self.report.no_face += 1
                return

            if len(faces) > 1:
                self.reject_manager.record(photo_path, "multiple_faces", f"detected {len(faces)}")
                self.report.multiple_faces += 1
                return

            height, width = image.shape[:2]
            thumbnail_path = None
            try:
                thumb_dir = self.workspace_path / "Thumbnails"
                thumb_dir.mkdir(parents=True, exist_ok=True)
                thumbnail_name = f"{sha256[:16]}.jpg"
                thumbnail_path = thumb_dir / thumbnail_name
                save_thumbnail(photo_path, thumbnail_path, 256)
            except Exception:
                pass

            primary_face = faces[0]
            bbox = primary_face.bbox.astype(int)
            qa = self.quality_analyzer.analyze(image, tuple(bbox))
            face_size = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
            if qa.blur_score < 50.0 and face_size < 60:
                self.reject_manager.record(photo_path, "too_small", f"size={face_size}, blur={qa.blur_score:.1f}")
                self.report.too_small += 1
                return

            person_dir = photo_path.parent
            display_name, extra_metadata = IdentityParser.parse_folder_name(person_dir.name)
            metadata_json = IdentityParser.build_metadata_json(extra_metadata)

            with get_session() as session:
                identity = session.query(Identity).filter_by(original_folder_name=person_dir.name).first()
                if identity is None:
                    self._person_counter += 1
                    identity = Identity(
                        person_id=f"{self._person_counter:09d}",
                        display_name=display_name,
                        original_folder_name=person_dir.name,
                        metadata_json=metadata_json,
                    )
                    session.add(identity)
                    session.flush()
                elif not identity.person_id:
                    self._person_counter += 1
                    identity.person_id = f"{self._person_counter:09d}"

                photo = Photo(
                    identity_id=identity.id,
                    file_path=str(photo_path),
                    sha256=sha256,
                    width=width,
                    height=height,
                    thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
                    is_primary=True,
                    quality_score=qa.total_score,
                )
                session.add(photo)
                session.flush()

                embed_t0 = time.perf_counter()
                embedding_vector = recognition.get_embedding(image, primary_face)
                embed_ms = (time.perf_counter() - embed_t0) * 1000
                self._embedding_times.append(embed_ms)

                embedding = Embedding(
                    photo_id=photo.id,
                    model_name="buffalo_l",
                )
                embedding.set_vector(embedding_vector)
                session.add(embedding)
                session.flush()

                qc = QualityCheck(
                    photo_id=photo.id,
                    blur_score=qa.blur_score,
                    face_size=qa.face_size,
                    yaw_angle=qa.yaw_angle,
                    pitch_angle=qa.pitch_angle,
                    confidence=qa.confidence,
                    is_good_quality=qa.is_good_quality,
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
                self.duplicate_detector._embeddings[photo.id] = embedding_vector
                self.result.imported += 1
                session.commit()

        except Exception as exc:
            logger.error(f"Error importing {photo_path}: {exc}")
            self.result.errors += 1

    def _inject_rejection(self, reason: str | None) -> None:
        reason = reason or "unknown"
        if reason == "cannot_read":
            self.report.cannot_read += 1
        elif reason == "corrupted":
            self.report.corrupted += 1
        elif reason == "empty_file":
            self.report.corrupted += 1
        else:
            self.report.other += 1

    def _count_photos(self, directories: list[Path]) -> int:
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        return sum(
            1 for d in directories
            for p in d.rglob("*")
            if p.is_file() and p.suffix.lower() in exts
        )
