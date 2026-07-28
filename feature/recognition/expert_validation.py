"""Expert validation for recognition results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from feature.recognition.pipeline import RecognitionPipeline
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex


class ExpertVerdict(str, Enum):
    TOP1_CORRECT = "top1_correct"
    IN_TOP3 = "in_top3"
    IN_TOP5 = "in_top5"
    IN_TOP10 = "in_top10"
    NOT_FOUND = "not_found"
    WRONG = "wrong"


@dataclass
class Candidate:
    rank: int
    photo_id: int
    distance: float
    similarity: float
    identity_name: str | None = None


@dataclass
class ExpertValidationResult:
    photo_path: Path
    verdict: ExpertVerdict
    correct_identity_id: int | None = None
    candidates: list[Candidate] = field(default_factory=list)
    notes: str | None = None


@dataclass
class ExpertValidationReport:
    total: int = 0
    top1_correct: int = 0
    in_top3: int = 0
    in_top5: int = 0
    in_top10: int = 0
    not_found: int = 0
    wrong: int = 0
    results: list[ExpertValidationResult] = field(default_factory=list)

    @property
    def top1_accuracy(self) -> float:
        return self.top1_correct / self.total if self.total > 0 else 0.0

    @property
    def top3_accuracy(self) -> float:
        return self.in_top3 / self.total if self.total > 0 else 0.0

    @property
    def top5_accuracy(self) -> float:
        return self.in_top5 / self.total if self.total > 0 else 0.0

    def print(self) -> None:
        print("\n" + "=" * 60)
        print("EXPERT VALIDATION REPORT")
        print("=" * 60)
        print(f"Total:            {self.total}")
        print(f"Top-1 correct:    {self.top1_correct} ({self.top1_accuracy:.1%})")
        print(f"Top-3 correct:    {self.in_top3} ({self.top3_accuracy:.1%})")
        print(f"Top-5 correct:    {self.in_top5} ({self.top5_accuracy:.1%})")
        print(f"Not found:        {self.not_found}")
        print(f"Wrong:            {self.wrong}")
        print("=" * 60 + "\n")


class ExpertValidator:
    def __init__(self, engine: RecognitionEngine, faiss: FaissIndex, top_k: int = 10) -> None:
        self.engine = engine
        self.faiss = faiss
        self.top_k = top_k
        self.report = ExpertValidationReport()

    def validate_photo(self, photo_path: Path, correct_identity_id: int | None = None) -> ExpertValidationResult:
        pipeline = RecognitionPipeline(self.engine, self.faiss)
        result = pipeline.process_photo(photo_path)

        candidates = []
        if result.candidates:
            for i, cand in enumerate(result.candidates[: self.top_k], 1):
                candidates.append(Candidate(
                    rank=i,
                    photo_id=cand.photo_id,
                    distance=cand.distance,
                    similarity=cand.similarity,
                    identity_name=cand.identity_name if hasattr(cand, 'identity_name') else None,
                ))

        if correct_identity_id is None:
            return ExpertValidationResult(
                photo_path=photo_path,
                verdict=ExpertVerdict.NOT_FOUND,
                candidates=candidates,
            )

        found_ranks = [c.rank for c in candidates if c.identity_name and str(correct_identity_id) in c.identity_name]
        if not found_ranks:
            verdict = ExpertVerdict.NOT_FOUND
        elif found_ranks[0] == 1:
            verdict = ExpertVerdict.TOP1_CORRECT
        elif found_ranks[0] <= 3:
            verdict = ExpertVerdict.IN_TOP3
        elif found_ranks[0] <= 5:
            verdict = ExpertVerdict.IN_TOP5
        elif found_ranks[0] <= 10:
            verdict = ExpertVerdict.IN_TOP10
        else:
            verdict = ExpertVerdict.NOT_FOUND

        return ExpertValidationResult(
            photo_path=photo_path,
            verdict=verdict,
            correct_identity_id=correct_identity_id,
            candidates=candidates,
        )

    def add_result(self, result: ExpertValidationResult) -> None:
        self.report.results.append(result)
        self.report.total += 1
        if result.verdict == ExpertVerdict.TOP1_CORRECT:
            self.report.top1_correct += 1
            self.report.in_top3 += 1
            self.report.in_top5 += 1
            self.report.in_top10 += 1
        elif result.verdict == ExpertVerdict.IN_TOP3:
            self.report.in_top3 += 1
            self.report.in_top5 += 1
            self.report.in_top10 += 1
        elif result.verdict == ExpertVerdict.IN_TOP5:
            self.report.in_top5 += 1
            self.report.in_top10 += 1
        elif result.verdict == ExpertVerdict.IN_TOP10:
            self.report.in_top10 += 1
        elif result.verdict == ExpertVerdict.NOT_FOUND:
            self.report.not_found += 1
        elif result.verdict == ExpertVerdict.WRONG:
            self.report.wrong += 1
