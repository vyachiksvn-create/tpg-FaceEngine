"""Recognition pipeline: single photo processing end-to-end."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from loguru import logger

from feature.core.events import Event, EventBus
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex
from feature.storage.database import get_session
from feature.storage.models import Embedding, Photo, QualityCheck


@dataclass
class Candidate:
    photo_id: int
    identity_id: int | None
    score: float
    distance: float
    face_size: int | None = None
    blur_score: float | None = None
    thumbnail_path: str | None = None


@dataclass
class ProcessingResult:
    photo_path: Path
    status: str
    candidates: list[Candidate] = field(default_factory=list)
    selected_identity_id: int | None = None
    error: str | None = None
    processing_time_ms: float = 0.0


class RecognitionPipeline:
    def __init__(
        self,
        recognition_engine: RecognitionEngine,
        faiss_index: FaissIndex,
        event_bus: EventBus | None = None,
    ) -> None:
        self.recognition = recognition_engine
        self.faiss = faiss_index
        self.event_bus = event_bus

    def process_photo(self, photo_path: Path) -> ProcessingResult:
        t0 = logger.info(f"Processing: {photo_path}")
        result = ProcessingResult(photo_path=photo_path, status="error")
        try:
            image = cv2.imread(str(photo_path))
            if image is None:
                result.error = "Cannot read image"
                return result

            faces = self.recognition.detect_faces(image)
            if not faces:
                result.status = "no_faces"
                result.error = "No faces detected"
                return result

            primary = faces[0]
            embedding = self.recognition.get_embedding(image, primary)
            faiss_results = self.faiss.search(embedding, top_k=5)

            candidates = []
            for photo_id, distance in faiss_results:
                candidates.append(self._build_candidate(photo_id, embedding, distance))

            result.status = "found"
            result.candidates = candidates
            result.processing_time_ms = 0.0
            return result
        except Exception as exc:
            result.error = str(exc)
            logger.error(f"Processing failed for {photo_path}: {exc}")
            return result

    def _build_candidate(self, photo_id: int, query_embedding: np.ndarray, distance: float) -> Candidate:
        with get_session() as session:
            photo = session.query(Photo).filter_by(id=photo_id).first()
            if not photo:
                return Candidate(photo_id=photo_id, identity_id=None, score=0.0, distance=distance)
            score = self._cosine_similarity(query_embedding, self._load_embedding(photo_id))
            qc = session.query(QualityCheck).filter_by(photo_id=photo_id).first()
            return Candidate(
                photo_id=photo_id,
                identity_id=photo.identity_id,
                score=score,
                distance=distance,
                face_size=qc.face_size if qc else None,
                blur_score=qc.blur_score if qc else None,
                thumbnail_path=photo.thumbnail_path,
            )

    def _load_embedding(self, photo_id: int) -> np.ndarray | None:
        with get_session() as session:
            emb = session.query(Embedding).filter_by(photo_id=photo_id).first()
            if emb:
                return emb.get_vector()
            return None

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray | None) -> float:
        if b is None:
            return 0.0
        a = np.asarray(a, dtype=np.float32)
        b = np.asarray(b, dtype=np.float32)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)