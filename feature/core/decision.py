from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np
from loguru import logger


@dataclass
class Candidate:
    identity_id: int | None
    photo_id: int
    distance: float
    score: float = 0.0
    votes: int = 0
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    identity_id: int | None
    confidence: float
    threshold_used: float
    strategy: str
    candidates: list[Candidate]
    explanation: dict[str, Any] = field(default_factory=dict)


class DecisionEngine:
    def __init__(self, config: Any) -> None:
        self.config = config
        self._history: list[DecisionResult] = []

    def decide(
        self,
        query_embedding: np.ndarray,
        search_results: list[tuple[int, float]],
        embeddings_map: dict[int, np.ndarray],
        strategy: str | None = None,
        threshold: float | None = None,
    ) -> DecisionResult:
        strategy = strategy or getattr(getattr(self.config, "search", None), "merge_strategy", "hybrid")
        threshold = threshold if threshold is not None else getattr(getattr(self.config, "recognition", None), "threshold", 0.6)
        t0 = time.perf_counter()

        candidates = self._build_candidates(search_results, embeddings_map, query_embedding)
        if not candidates:
            return DecisionResult(
                identity_id=None,
                confidence=0.0,
                threshold_used=threshold,
                strategy=strategy,
                candidates=[],
                explanation={"reason": "no_candidates"},
            )

        if strategy == "max":
            result = self._strategy_max(candidates, threshold)
        elif strategy == "vote":
            result = self._strategy_vote(candidates, threshold)
        else:
            result = self._strategy_hybrid(candidates, threshold)

        elapsed = time.perf_counter() - t0
        result.explanation["elapsed_ms"] = round(elapsed * 1000, 3)
        result.explanation["candidates_count"] = len(candidates)
        result.explanation["strategy"] = strategy
        self._history.append(result)
        return result

    def _build_candidates(
        self,
        search_results: list[tuple[int, float]],
        embeddings_map: dict[int, np.ndarray],
        query_embedding: np.ndarray,
    ) -> list[Candidate]:
        candidates: list[Candidate] = []
        for photo_id, distance in search_results:
            emb = embeddings_map.get(photo_id)
            score = self._cosine_similarity(query_embedding, emb) if emb is not None else 0.0
            candidates.append(
                Candidate(
                    photo_id=photo_id,
                    identity_id=None,
                    distance=distance,
                    score=score,
                )
            )
        return candidates

    def _strategy_max(self, candidates: list[Candidate], threshold: float) -> DecisionResult:
        best = max(candidates, key=lambda c: c.score)
        identity_id = best.identity_id
        confidence = best.score
        passed = confidence >= threshold
        return DecisionResult(
            identity_id=identity_id if passed else None,
            confidence=confidence,
            threshold_used=threshold,
            strategy="max",
            candidates=candidates,
            explanation={"reason": "max_score", "best_photo_id": best.photo_id},
        )

    def _strategy_vote(self, candidates: list[Candidate], threshold: float) -> DecisionResult:
        votes: dict[int | None, int] = {}
        scores: dict[int | None, float] = {}
        for c in candidates:
            votes[c.identity_id] = votes.get(c.identity_id, 0) + 1
            scores[c.identity_id] = scores.get(c.identity_id, 0.0) + c.score
        if not votes:
            return self._strategy_max(candidates, threshold)
        best_identity = max(votes, key=lambda k: (votes[k], scores[k]))
        total_votes = votes[best_identity]
        confidence = scores[best_identity] / total_votes if total_votes else 0.0
        passed = confidence >= threshold
        return DecisionResult(
            identity_id=best_identity if passed else None,
            confidence=confidence,
            threshold_used=threshold,
            strategy="vote",
            candidates=candidates,
            explanation={
                "reason": "voting",
                "votes": votes,
                "total_candidates": len(candidates),
            },
        )

    def _strategy_hybrid(self, candidates: list[Candidate], threshold: float) -> DecisionResult:
        best = max(candidates, key=lambda c: c.score)
        votes: dict[int | None, int] = {}
        for c in candidates:
            votes[c.identity_id] = votes.get(c.identity_id, 0) + 1
        support = votes.get(best.identity_id, 0)
        max_votes = max(votes.values()) if votes else 1
        vote_ratio = support / max_votes
        confidence = 0.6 * best.score + 0.4 * vote_ratio
        passed = confidence >= threshold
        return DecisionResult(
            identity_id=best.identity_id if passed else None,
            confidence=confidence,
            threshold_used=threshold,
            strategy="hybrid",
            candidates=candidates,
            explanation={
                "reason": "hybrid",
                "best_score": best.score,
                "vote_ratio": vote_ratio,
                "support": support,
                "best_photo_id": best.photo_id,
            },
        )

    def explain(self, result: DecisionResult) -> str:
        if result.identity_id is None:
            return f"Совпадение не найдено. Лучший score={result.confidence:.3f}, порог={result.threshold_used}"
        parts = [
            f"Идентичность: {result.identity_id}",
            f"Уверенность: {result.confidence:.3f}",
            f"Стратегия: {result.strategy}",
        ]
        if "best_photo_id" in result.explanation:
            parts.append(f"Лучшее фото: {result.explanation['best_photo_id']}")
        if "votes" in result.explanation:
            parts.append(f"Голосов: {result.explanation['votes']}")
        return " | ".join(parts)

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