"""Threshold analysis combining calibration and expert validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class ThresholdAnalysis:
    threshold: float = 0.5
    recall: float = 0.0
    precision: float = 0.0
    f1: float = 0.0
    false_positives: int = 0
    false_negatives: int = 0
    policy: str = "balanced"


class ThresholdAnalyzer:
    def __init__(self, same_person_distances: list[float], diff_person_distances: list[float]) -> None:
        self.same = np.array(same_person_distances, dtype=np.float32)
        self.diff = np.array(diff_person_distances, dtype=np.float32)

    def analyze(self, threshold: float) -> ThresholdAnalysis:
        tp = int(np.sum(self.same <= threshold))
        fn = int(np.sum(self.same > threshold))
        fp = int(np.sum(self.diff <= threshold))
        tn = int(np.sum(self.diff > threshold))

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        if precision > 0.95:
            policy = "conservative"
        elif recall < 0.8:
            policy = "aggressive"
        else:
            policy = "balanced"

        return ThresholdAnalysis(
            threshold=threshold,
            recall=recall,
            precision=precision,
            f1=f1,
            false_positives=fp,
            false_negatives=fn,
            policy=policy,
        )

    def find_best(self) -> ThresholdAnalysis:
        best = None
        best_score = -1.0
        if self.same.size == 0 or self.diff.size == 0:
            return ThresholdAnalysis()
        for thr in np.linspace(0.01, 1.0, 200):
            analysis = self.analyze(float(thr))
            score = analysis.f1
            if score > best_score:
                best_score = score
                best = analysis
        return best or ThresholdAnalysis()
