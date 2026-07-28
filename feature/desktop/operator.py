"""Operator Desktop MVP foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from feature.recognition.decision_explanation import DecisionExplanation
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex
from feature.storage.database import get_session
from feature.storage.models import Identity, Photo


class OperatorAction(str, Enum):
    CONFIRM = "confirm"
    NEW_IDENTITY = "new_identity"
    SKIP = "skip"
    MERGE = "merge"


@dataclass
class IdentityCard:
    identity_id: int
    display_name: str | None
    photo_count: int
    representative_photo_path: str | None
    health_score: float | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OperatorSession:
    current_photo_path: Path | None = None
    current_explanation: DecisionExplanation | None = None
    current_identity_card: IdentityCard | None = None
    processed_count: int = 0
    confirmed_count: int = 0
    new_identity_count: int = 0
    skipped_count: int = 0


class OperatorDesktop:
    def __init__(self, engine: RecognitionEngine, faiss: FaissIndex) -> None:
        self.engine = engine
        self.faiss = faiss
        self.session = OperatorSession()
        self._identity_cache: dict[int, IdentityCard] = {}

    def load_photo(self, photo_path: Path) -> DecisionExplanation:
        from feature.recognition.pipeline import RecognitionPipeline
        import time
        t0 = time.perf_counter()
        pipeline = RecognitionPipeline(self.engine, self.faiss)
        result = pipeline.process_photo(photo_path)
        elapsed = (time.perf_counter() - t0) * 1000

        search_results = [(c.photo_id, c.distance) for c in result.candidates] if result.candidates else []
        identity_stats = self._collect_identity_stats(search_results)
        explainer = self._get_explainer()
        explanation = explainer.explain(photo_path, search_results, identity_stats, elapsed)
        self.session.current_photo_path = photo_path
        self.session.current_explanation = explanation
        self.session.processed_count += 1
        return explanation

    def get_identity_card(self, identity_id: int) -> IdentityCard | None:
        if identity_id in self._identity_cache:
            return self._identity_cache[identity_id]
        try:
            with get_session() as session:
                identity = session.query(Identity).filter_by(id=identity_id).first()
                if not identity:
                    return None
                photo_count = session.query(Photo).filter_by(identity_id=identity_id).count()
                card = IdentityCard(
                    identity_id=identity.id,
                    display_name=identity.display_name,
                    photo_count=photo_count,
                    representative_photo_path=identity.representative_photo_id,
                    health_score=identity.health_score,
                    metadata={"original_folder_name": identity.original_folder_name},
                )
                self._identity_cache[identity_id] = card
                return card
        except Exception:
            return None

    def confirm(self, identity_id: int | None = None) -> OperatorAction:
        self.session.confirmed_count += 1
        if identity_id is not None:
            self._invalidate_cache(identity_id)
        return OperatorAction.CONFIRM

    def create_new_identity(self, display_name: str | None = None) -> OperatorAction:
        self.session.new_identity_count += 1
        return OperatorAction.NEW_IDENTITY

    def skip(self) -> OperatorAction:
        self.session.skipped_count += 1
        return OperatorAction.SKIP

    def get_stats(self) -> dict[str, int]:
        return {
            "processed": self.session.processed_count,
            "confirmed": self.session.confirmed_count,
            "new_identity": self.session.new_identity_count,
            "skipped": self.session.skipped_count,
        }

    def _collect_identity_stats(self, search_results: list[tuple[int, float]]) -> dict[int, dict[str, Any]]:
        stats: dict[int, dict[str, Any]] = {}
        try:
            with get_session() as session:
                for photo_id, _ in search_results:
                    photo = session.query(Photo).filter_by(id=photo_id).first()
                    if photo and photo.identity_id not in stats:
                        identity = session.query(Identity).filter_by(id=photo.identity_id).first()
                        photo_count = session.query(Photo).filter_by(identity_id=photo.identity_id).count()
                        stats[photo.identity_id] = {
                            "photo_id": photo_id,
                            "display_name": identity.display_name if identity else None,
                            "photo_count": photo_count,
                            "avg_quality": 0.0,
                            "health_score": identity.health_score if identity else None,
                        }
        except Exception:
            pass
        return stats

    def _get_explainer(self) -> Any:
        from feature.recognition.decision_explanation import DecisionExplainer
        return DecisionExplainer()

    def _invalidate_cache(self, identity_id: int) -> None:
        self._identity_cache.pop(identity_id, None)
