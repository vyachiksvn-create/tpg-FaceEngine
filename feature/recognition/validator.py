"""Recognition validation and metrics collection."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger

from feature.recognition.pipeline import RecognitionPipeline
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex
from feature.storage.database import get_session
from feature.storage.models import Identity, Photo


@dataclass
class CandidateResult:
    photo_id: int
    identity_id: int | None
    distance: float
    similarity: float


@dataclass
class PhotoValidationResult:
    photo_path: Path
    status: str
    candidates: list[CandidateResult] = field(default_factory=list)
    top1_distance: float | None = None
    top1_identity_id: int | None = None
    processing_time_ms: float = 0.0
    error: str | None = None


@dataclass
class ValidationReport:
    total_photos: int = 0
    processed: int = 0
    found: int = 0
    not_found: int = 0
    errors: int = 0
    avg_top1_distance: float = 0.0
    avg_top5_distance: float = 0.0
    avg_processing_time_ms: float = 0.0
    distance_distribution: dict[str, int] = field(default_factory=dict)
    all_results: list[PhotoValidationResult] = field(default_factory=list)

    def print(self) -> None:
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(f"Total photos:      {self.total_photos}")
        print(f"Processed:         {self.processed}")
        print(f"Found:             {self.found}")
        print(f"Not found:         {self.not_found}")
        print(f"Errors:            {self.errors}")
        print("-" * 60)
        if self.processed > 0:
            print(f"Avg Top1 distance: {self.avg_top1_distance:.4f}")
            print(f"Avg Top5 distance: {self.avg_top5_distance:.4f}")
            print(f"Avg pipeline:      {self.avg_processing_time_ms:.1f} ms")
        print("-" * 60)
        if self.distance_distribution:
            print("Distance distribution:")
            for bucket, count in sorted(self.distance_distribution.items()):
                bar = "#" * min(count // 5, 50)
                print(f"  {bucket}: {count:4d} {bar}")
        print("=" * 60 + "\n")


class RecognitionValidator:
    def __init__(self, engine: RecognitionEngine, faiss: FaissIndex, top_k: int = 10) -> None:
        self.engine = engine
        self.faiss = faiss
        self.top_k = top_k
        self.report = ValidationReport()

    def validate_unknown_folder(self, unknown_path: Path, limit: int | None = None) -> ValidationReport:
        files = [
            p for p in unknown_path.rglob("*")
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        if limit:
            files = files[:limit]
        self.report.total_photos = len(files)
        logger.info(f"Validation started: {len(files)} photos")

        for photo_path in files:
            result = self._validate_photo(photo_path)
            self.report.all_results.append(result)
            self.report.processed += 1
            if result.status == "found":
                self.report.found += 1
                if result.top1_distance is not None:
                    self._update_distance_stats(result.top1_distance)
            elif result.status == "no_faces":
                self.report.not_found += 1
            else:
                self.report.errors += 1

        self._compute_averages()
        self.report.print()
        logger.info(
            f"Validation finished: found={self.report.found}, "
            f"not_found={self.report.not_found}, errors={self.report.errors}"
        )
        return self.report

    def _validate_photo(self, photo_path: Path) -> PhotoValidationResult:
        import time
        t0 = time.perf_counter()
        result = PhotoValidationResult(photo_path=photo_path, status="error")
        try:
            import cv2
            image = cv2.imread(str(photo_path))
            if image is None:
                result.error = "Cannot read image"
                return result

            faces = self.engine.detect_faces(image)
            if not faces:
                result.status = "no_faces"
                result.error = "No faces detected"
                result.processing_time_ms = (time.perf_counter() - t0) * 1000
                return result

            primary = faces[0]
            embedding = self.engine.get_embedding(image, primary)
            faiss_results = self.faiss.search(embedding, top_k=self.top_k)

            candidates = []
            for photo_id, distance in faiss_results:
                candidates.append(CandidateResult(
                    photo_id=photo_id,
                    identity_id=self._get_identity_id_by_photo(photo_id),
                    distance=distance,
                    similarity=1.0 / (1.0 + distance),
                ))

            result.status = "found"
            result.candidates = candidates
            result.top1_distance = candidates[0].distance if candidates else None
            result.top1_identity_id = candidates[0].identity_id if candidates else None
            result.processing_time_ms = (time.perf_counter() - t0) * 1000
            return result
        except Exception as exc:
            result.error = str(exc)
            result.processing_time_ms = (time.perf_counter() - t0) * 1000
            return result

    def _get_identity_id_by_photo(self, photo_id: int) -> int | None:
        try:
            with get_session() as session:
                photo = session.query(Photo).filter_by(id=photo_id).first()
                if photo:
                    return photo.identity_id
        except Exception:
            pass
        return None

    def _update_distance_stats(self, distance: float) -> None:
        bucket = f"{distance:.2f}"
        self.report.distance_distribution[bucket] = self.report.distance_distribution.get(bucket, 0) + 1

    def _compute_averages(self) -> None:
        top1_distances = [r.top1_distance for r in self.report.all_results if r.top1_distance is not None]
        if top1_distances:
            self.report.avg_top1_distance = float(np.mean(top1_distances))

        top5_distances = []
        for r in self.report.all_results:
            if len(r.candidates) >= 5:
                top5_distances.append(np.mean([c.distance for c in r.candidates[:5]]))
        if top5_distances:
            self.report.avg_top5_distance = float(np.mean(top5_distances))

        times = [r.processing_time_ms for r in self.report.all_results]
        if times:
            self.report.avg_processing_time_ms = float(np.mean(times))
