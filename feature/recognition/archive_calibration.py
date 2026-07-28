"""Archive calibration: intra-identity and inter-identity distance analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger

from feature.storage.database import get_session
from feature.storage.models import Embedding, Identity, Photo


@dataclass
class CalibrationReport:
    identities_with_embeddings: int = 0
    total_embeddings: int = 0
    intra_distances: list[float] = field(default_factory=list)
    inter_distances: list[float] = field(default_factory=list)
    same_person_mean: float = 0.0
    same_person_std: float = 0.0
    diff_person_mean: float = 0.0
    diff_person_std: float = 0.0
    recommended_threshold: float = 0.0

    def print(self) -> None:
        print("\n" + "=" * 60)
        print("ARCHIVE CALIBRATION REPORT")
        print("=" * 60)
        print(f"Identities:       {self.identities_with_embeddings}")
        print(f"Embeddings:       {self.total_embeddings}")
        print("-" * 60)
        if self.intra_distances:
            print(f"Same person  mean: {self.same_person_mean:.4f}")
            print(f"Same person  std:  {self.same_person_std:.4f}")
            print(f"Same person  min:  {min(self.intra_distances):.4f}")
            print(f"Same person  max:  {max(self.intra_distances):.4f}")
        print("-" * 60)
        if self.inter_distances:
            print(f"Diff person  mean: {self.diff_person_mean:.4f}")
            print(f"Diff person  std:  {self.diff_person_std:.4f}")
            print(f"Diff person  min:  {min(self.inter_distances):.4f}")
            print(f"Diff person  max:  {max(self.inter_distances):.4f}")
        print("-" * 60)
        print(f"Recommended threshold: {self.recommended_threshold:.4f}")
        print("=" * 60 + "\n")


class ArchiveCalibration:
    def __init__(self, max_samples: int = 5000) -> None:
        self.max_samples = max_samples
        self.report = CalibrationReport()

    def calibrate(self) -> CalibrationReport:
        self.report = CalibrationReport()
        try:
            with get_session() as session:
                identities = session.query(Identity).all()
                identity_embeddings: dict[int, list[np.ndarray]] = {}
                for identity in identities:
                    photos = session.query(Photo).filter_by(identity_id=identity.id).all()
                    vecs = []
                    for photo in photos:
                        emb = session.query(Embedding).filter_by(photo_id=photo.id).first()
                        if emb is not None:
                            vec = emb.get_vector()
                            if vec is not None and vec.size > 0:
                                vecs.append(np.array(vec, dtype=np.float32))
                    if vecs:
                        identity_embeddings[identity.id] = vecs

                self.report.identities_with_embeddings = len(identity_embeddings)
                self.report.total_embeddings = sum(len(v) for v in identity_embeddings.values())

                for identity_id, vecs in identity_embeddings.items():
                    if len(vecs) < 2:
                        continue
                    for i in range(len(vecs) - 1):
                        for j in range(i + 1, len(vecs)):
                            dist = float(np.linalg.norm(vecs[i] - vecs[j]))
                            self.report.intra_distances.append(dist)

                ids = list(identity_embeddings.keys())
                for idx_a in range(min(len(ids), 100)):
                    for idx_b in range(idx_a + 1, min(len(ids), 100)):
                        vecs_a = identity_embeddings[ids[idx_a]]
                        vecs_b = identity_embeddings[ids[idx_b]]
                        for va in vecs_a[:5]:
                            for vb in vecs_b[:5]:
                                dist = float(np.linalg.norm(va - vb))
                                self.report.inter_distances.append(dist)

                if self.report.intra_distances:
                    self.report.same_person_mean = float(np.mean(self.report.intra_distances))
                    self.report.same_person_std = float(np.std(self.report.intra_distances))
                if self.report.inter_distances:
                    self.report.diff_person_mean = float(np.mean(self.report.inter_distances))
                    self.report.diff_person_std = float(np.std(self.report.inter_distances))

                self.report.recommended_threshold = self._recommend()
        except Exception as exc:
            logger.warning(f"Calibration failed: {exc}")

        self.report.print()
        return self.report

    def _recommend(self) -> float:
        if not self.report.intra_distances or not self.report.inter_distances:
            return 0.5
        intra = np.array(self.report.intra_distances)
        inter = np.array(self.report.inter_distances)
        candidates = []
        for thr in np.linspace(float(inter.min()), float(inter.max()), 200):
            tp = float(np.mean(intra <= thr))
            fp = float(np.mean(inter <= thr))
            if fp == 0:
                score = tp
            else:
                score = tp / (tp + fp)
            candidates.append((score, thr))
        candidates.sort(reverse=True)
        return float(candidates[0][1]) if candidates else 0.5
