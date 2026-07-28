from __future__ import annotations

from pathlib import Path
from typing import Any

import faiss
import numpy as np
from loguru import logger


class FaissIndex:
    def __init__(self, config: Any = None, dimension: int = 512) -> None:
        self.config = config
        self.dimension = dimension
        self._index: faiss.Index | None = None
        self._id_map: dict[int, int] = {}
        self._reverse_id_map: dict[int, int] = {}
        self._next_id = 0

    def create_index(self, index_type: str = "flat") -> None:
        if index_type == "flat":
            self._index = faiss.IndexFlatL2(self.dimension)
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatL2(self.dimension)
            self._index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif index_type == "hnsw":
            self._index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Неподдерживаемый тип индекса: {index_type}")
        logger.info(f"Faiss индекс создан: {index_type}, размерность: {self.dimension}")

    def add_vectors(self, vectors: np.ndarray, ids: list[int]) -> None:
        if self._index is None:
            self.create_index()
        vectors = np.array(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        self._index.add(vectors)
        for idx in ids:
            self._id_map[idx] = self._next_id
            self._reverse_id_map[self._next_id] = idx
            self._next_id += 1
        logger.debug(f"Добавлено {len(ids)} векторов в индекс")

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[tuple[int, float]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        query_vector = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        distances, indices = self._index.search(query_vector, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            original_id = self._reverse_id_map.get(idx)
            if original_id is not None:
                results.append((original_id, float(dist)))
        return results

    def remove_vector(self, photo_id: int) -> None:
        if photo_id not in self._id_map:
            return
        index_id = self._id_map[photo_id]
        if self._index is not None:
            self._index.remove_ids(np.array([index_id], dtype=np.int64))
        del self._id_map[photo_id]
        del self._reverse_id_map[index_id]
        logger.debug(f"Вектор удален из индекса: {photo_id}")

    def save(self, index_path: str, id_map_path: str) -> None:
        if self._index is None:
            raise RuntimeError("Индекс не создан")
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, index_path)
        import json
        with open(id_map_path, "w", encoding="utf-8") as f:
            json.dump({"id_map": self._id_map, "next_id": self._next_id}, f)
        logger.info(f"Faiss индекс сохранен: {index_path}")

    def load(self, index_path: str, id_map_path: str) -> None:
        if not Path(index_path).exists():
            raise FileNotFoundError(f"Файл индекса не найден: {index_path}")
        self._index = faiss.read_index(index_path)
        import json
        with open(id_map_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._id_map = {int(k): int(v) for k, v in data.get("id_map", {}).items()}
        self._reverse_id_map = {int(v): int(k) for k, v in self._id_map.items()}
        self._next_id = data.get("next_id", max(self._reverse_id_map.keys()) + 1 if self._reverse_id_map else 0)
        self.dimension = self._index.d
        logger.info(f"Faiss индекс загружен: {index_path}, векторов: {self._index.ntotal}")

    @property
    def total_vectors(self) -> int:
        return self._index.ntotal if self._index else 0
