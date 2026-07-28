"""Automatic threshold tuning based on validation data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class ThresholdRecommendation:
    operator_threshold: float = 0.42
    auto_confirm_threshold: float = 0.22
    search_threshold: float = 0.60
    top_k: int = 10
    expected_recall: float = 0.0
    expected_precision: float = 0.0
    policy: str = "balanced"


class ThresholdTuner:
    def __init__(self, distances: list[float]) -> None:
        self.distances = np.array(distances, dtype=np.float32)

    def recommend(self) -> ThresholdRecommendation:
        rec = ThresholdRecommendation()
        if len(self.distances) == 0:
            return rec

        distances = self.distances
        min_dist = float(distances.min())
        max_dist = float(distances.max())
        median = float(np.median(distances))
        mean = float(np.mean(distances))
        std = float(np.std(distances))

        operator_threshold = min(median + std * 0.5, max_dist * 0.8)
        operator_threshold = max(operator_threshold, min_dist + 0.05)
        operator_threshold = min(operator_threshold, 0.8)

        auto_confirm_threshold = min(mean - std * 0.5, min_dist + 0.1)
        auto_confirm_threshold = max(auto_confirm_threshold, min_dist)
        auto_confirm_threshold = min(auto_confirm_threshold, operator_threshold - 0.05)

        search_threshold = max(operator_threshold * 1.5, 0.6)
        search_threshold = min(search_threshold, 1.2)

        rec.operator_threshold = round(float(operator_threshold), 4)
        rec.auto_confirm_threshold = round(float(auto_confirm_threshold), 4)
        rec.search_threshold = round(float(search_threshold), 4)
        rec.top_k = 10
        rec.expected_recall = self._estimate_recall(rec.operator_threshold)
        rec.expected_precision = self._estimate_precision(rec.operator_threshold)

        if rec.expected_precision > 0.95:
            rec.policy = "conservative"
        elif rec.expected_precision < 0.85:
            rec.policy = "aggressive"
        else:
            rec.policy = "balanced"

        return rec

    def _estimate_recall(self, threshold: float) -> float:
        if len(self.distances) == 0:
            return 0.0
        return float(np.mean(self.distances <= threshold))

    def _estimate_precision(self, threshold: float) -> float:
        if len(self.distances) == 0:
            return 0.0
        accepted = self.distances[self.distances <= threshold]
        if len(accepted) == 0:
            return 0.0
        return float(np.mean(accepted <= threshold))

    def print_recommendation(self, rec: ThresholdRecommendation) -> None:
        print("\n" + "=" * 60)
        print("THRESHOLD RECOMMENDATION")
        print("=" * 60)
        print(f"Policy:            {rec.policy}")
        print(f"Operator threshold:{rec.operator_threshold:.4f}")
        print(f"Auto confirm:      {rec.auto_confirm_threshold:.4f}")
        print(f"Search threshold:  {rec.search_threshold:.4f}")
        print(f"Top-K:             {rec.top_k}")
        print(f"Expected recall:   {rec.expected_recall:.2%}")
        print(f"Expected precision:{rec.expected_precision:.2%}")
        print("=" * 60 + "\n")
