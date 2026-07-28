"""Decision explanation API for structured recognition results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class CandidateExplanation:
    rank: int
    photo_id: int
    identity_id: int | None
    display_name: str | None
    distance: float
    similarity: float
    confidence: str
    photo_count: int = 0
    avg_quality: float = 0.0


@dataclass
class DecisionExplanation:
    photo_path: Path
    decision: str
    confidence: str
    similarity: float
    threshold: float
    top_candidate: CandidateExplanation | None = None
    candidates: list[CandidateExplanation] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    pipeline_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "photo_path": str(self.photo_path),
            "decision": self.decision,
            "confidence": self.confidence,
            "similarity": self.similarity,
            "threshold": self.threshold,
            "top_candidate": self.top_candidate.__dict__ if self.top_candidate else None,
            "candidates": [c.__dict__ for c in self.candidates],
            "evidence": self.evidence,
            "pipeline_time_ms": self.pipeline_time_ms,
        }


class DecisionExplainer:
    def __init__(self, operator_threshold: float = 0.1938, auto_confirm_threshold: float = 0.1438) -> None:
        self.operator_threshold = operator_threshold
        self.auto_confirm_threshold = auto_confirm_threshold

    def explain(self, photo_path: Path, search_results: list[tuple[int, float]], identity_stats: dict[int, dict[str, Any]] | None = None, pipeline_time_ms: float = 0.0) -> DecisionExplanation:
        candidates = self._build_candidates(search_results, identity_stats)
        top = candidates[0] if candidates else None
        similarity = top.similarity if top else 0.0
        distance = top.distance if top else float("inf")

        if similarity >= (1.0 - self.auto_confirm_threshold):
            decision = "auto_confirm"
            confidence = "very_high"
        elif distance <= self.operator_threshold:
            decision = "candidate"
            confidence = "high" if distance < self.operator_threshold * 0.8 else "medium"
        elif distance <= self.operator_threshold * 1.5:
            decision = "review"
            confidence = "low"
        else:
            decision = "unknown"
            confidence = "none"

        evidence = {
            "photos_compared": len(search_results),
            "best_match": distance,
            "threshold": self.operator_threshold,
            "auto_confirm_threshold": self.auto_confirm_threshold,
        }
        if top and identity_stats and top.identity_id in identity_stats:
            stats = identity_stats[top.identity_id]
            evidence.update({
                "photos_in_identity": stats.get("photo_count", 0),
                "average_quality": stats.get("avg_quality", 0.0),
                "identity_health": stats.get("health_score", 0.0),
            })

        return DecisionExplanation(
            photo_path=photo_path,
            decision=decision,
            confidence=confidence,
            similarity=similarity,
            threshold=self.operator_threshold,
            top_candidate=top,
            candidates=candidates[:5],
            evidence=evidence,
            pipeline_time_ms=pipeline_time_ms,
        )

    def _build_candidates(self, search_results: list[tuple[int, float]], identity_stats: dict[int, dict[str, Any]] | None) -> list[CandidateExplanation]:
        candidates: list[CandidateExplanation] = []
        for rank, (photo_id, distance) in enumerate(search_results, 1):
            similarity = 1.0 / (1.0 + distance)
            identity_id = None
            display_name = None
            photo_count = 0
            avg_quality = 0.0
            if identity_stats:
                for id_key, stats in identity_stats.items():
                    if stats.get("photo_id") == photo_id:
                        identity_id = id_key
                        display_name = stats.get("display_name")
                        photo_count = stats.get("photo_count", 0)
                        avg_quality = stats.get("avg_quality", 0.0)
                        break

            if distance < 0.2:
                conf = "very_high"
            elif distance < 0.35:
                conf = "high"
            elif distance < 0.5:
                conf = "medium"
            else:
                conf = "low"

            candidates.append(CandidateExplanation(
                rank=rank,
                photo_id=photo_id,
                identity_id=identity_id,
                display_name=display_name,
                distance=distance,
                similarity=similarity,
                confidence=conf,
                photo_count=photo_count,
                avg_quality=avg_quality,
            ))
        return candidates
