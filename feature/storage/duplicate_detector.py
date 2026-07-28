"""Duplicate detection based on embedding similarity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from loguru import logger

from feature.storage.models import Embedding


@dataclass
class DuplicateCandidate:
    photo_id_a: int
    photo_id_b: int
    identity_id_a: int | None
    identity_id_b: int | None
    distance: float
    similarity: float
    is_duplicate: bool = False


class DuplicateDetector:
    def __init__(self, threshold: float = 0.6) -> None:
        self.threshold = threshold
        self._embeddings: dict[int, np.ndarray] = {}

    def load_embeddings(self, embeddings: list[Embedding]) -> None:
        for emb in embeddings:
            vec = emb.get_vector()
            if vec is not None and vec.size > 0:
                self._embeddings[emb.photo_id] = vec

    def find_duplicates(self, photo_id: int, embedding: np.ndarray, top_k: int = 5) -> list[DuplicateCandidate]:
        candidates: list[DuplicateCandidate] = []
        query = np.array(embedding, dtype=np.float32).reshape(1, -1)
        for pid, vec in self._embeddings.items():
            if pid == photo_id:
                continue
            dist = float(np.linalg.norm(query - vec))
            similarity = 1.0 / (1.0 + dist)
            if dist < self.threshold:
                candidates.append(
                    DuplicateCandidate(
                        photo_id_a=photo_id,
                        photo_id_b=pid,
                        identity_id_a=None,
                        identity_id_b=None,
                        distance=dist,
                        similarity=similarity,
                        is_duplicate=True,
                    )
                )
        candidates.sort(key=lambda c: c.distance)
        return candidates[:top_k]

    def find_within_identity(self, photo_embeddings: list[tuple[int, np.ndarray]]) -> list[DuplicateCandidate]:
        candidates: list[DuplicateCandidate] = []
        for i, (pid_a, vec_a) in enumerate(photo_embeddings):
            for pid_b, vec_b in photo_embeddings[i + 1:]:
                dist = float(np.linalg.norm(np.array(vec_a, dtype=np.float32) - np.array(vec_b, dtype=np.float32)))
                similarity = 1.0 / (1.0 + dist)
                if dist < self.threshold:
                    candidates.append(
                        DuplicateCandidate(
                            photo_id_a=pid_a,
                            photo_id_b=pid_b,
                            identity_id_a=None,
                            identity_id_b=None,
                            distance=dist,
                            similarity=similarity,
                            is_duplicate=True,
                        )
                    )
        candidates.sort(key=lambda c: c.distance)
        return candidates
