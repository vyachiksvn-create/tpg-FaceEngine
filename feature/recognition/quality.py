"""Unified face quality analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


@dataclass
class QualityScore:
    blur_score: float = 0.0
    face_size: int = 0
    yaw_angle: float = 0.0
    pitch_angle: float = 0.0
    confidence: float = 0.0
    brightness: float = 0.0
    total_score: float = 0.0
    is_good_quality: bool = False


class QualityAnalyzer:
    def __init__(self) -> None:
        self.min_face_size = 80
        self.max_blur_threshold = 100.0
        self.max_yaw_angle = 30.0
        self.max_pitch_angle = 20.0
        self.min_confidence = 0.5

    def analyze(self, image: np.ndarray, face_box: tuple[int, int, int, int]) -> QualityScore:
        x1, y1, x2, y2 = face_box
        face_crop = image[y1:y2, x1:x2]

        score = QualityScore()
        if face_crop.size == 0:
            return score

        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        score.blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        score.face_size = max(x2 - x1, y2 - y1)
        score.brightness = float(np.mean(gray))

        face_w = max(x2 - x1, 1)
        face_h = max(y2 - y1, 1)
        aspect_ratio = face_w / face_h
        if aspect_ratio > 1.2 or aspect_ratio < 0.6:
            score.blur_score *= 0.8

        size_score = min(score.face_size / 150.0, 1.0)
        blur_score_norm = min(score.blur_score / 200.0, 1.0)
        brightness_score = 1.0 - abs(score.brightness - 128) / 128.0
        brightness_score = max(0.0, brightness_score)

        score.total_score = (size_score * 0.35 + blur_score_norm * 0.45 + brightness_score * 0.2) * 100
        score.is_good_quality = (
            score.face_size >= self.min_face_size
            and score.blur_score > self.max_blur_threshold
            and score.brightness > 40
            and score.brightness < 220
        )

        return score

    def select_best_photo(self, photos: list[tuple[np.ndarray, tuple[int, int, int, int], Any]]) -> tuple[np.ndarray, tuple[int, int, int, int], Any] | None:
        best = None
        best_score = -1.0
        for image, face_box, meta in photos:
            score = self.analyze(image, face_box)
            if score.total_score > best_score:
                best_score = score.total_score
                best = (image, face_box, meta)
        return best
