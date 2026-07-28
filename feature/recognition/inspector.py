"""Interactive candidate inspector for recognition results."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from feature.recognition.pipeline import RecognitionPipeline
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex
from feature.storage.database import get_session
from feature.storage.models import Identity, Photo


class CandidateInspector:
    def __init__(self, engine: RecognitionEngine, faiss: FaissIndex) -> None:
        self.engine = engine
        self.faiss = faiss

    def inspect(self, photo_path: Path, top_k: int = 10) -> None:
        pipeline = RecognitionPipeline(self.engine, self.faiss)
        result = pipeline.process_photo(photo_path)
        print("\n" + "=" * 60)
        print(f"CANDIDATE INSPECTOR: {photo_path}")
        print("=" * 60)
        print(f"Status: {result.status}")
        if result.error:
            print(f"Error: {result.error}")
        if result.candidates:
            print("\nTop candidates:")
            for i, cand in enumerate(result.candidates[:top_k], 1):
                identity = self._get_identity_by_photo(cand.photo_id)
                name = identity.display_name if identity else f"Photo#{cand.photo_id}"
                print(
                    f"  {i}. {name:40s} "
                    f"distance={cand.distance:.4f} similarity={cand.similarity:.2%}"
                )
        print("=" * 60 + "\n")

    def _get_identity_by_photo(self, photo_id: int) -> Identity | None:
        try:
            with get_session() as session:
                photo = session.query(Photo).filter_by(id=photo_id).first()
                if photo and photo.identity_id:
                    return session.query(Identity).filter_by(id=photo.identity_id).first()
        except Exception:
            pass
        return None
