from __future__ import annotations

import numpy as np
import pytest

from feature.search.index import FaissIndex


class TestFaissIndex:
    def test_create_flat_index(self):
        index = FaissIndex(dimension=512)
        index.create_index("flat")
        assert index.total_vectors == 0

    def test_add_and_search(self):
        index = FaissIndex(dimension=512)
        vectors = np.random.randn(10, 512).astype(np.float32)
        ids = list(range(10))
        index.add_vectors(vectors, ids)
        assert index.total_vectors == 10
        query = vectors[0]
        results = index.search(query, top_k=3)
        assert len(results) == 3
        assert results[0][0] == 0

    def test_remove_vector(self):
        index = FaissIndex(dimension=512)
        vectors = np.random.randn(10, 512).astype(np.float32)
        ids = list(range(10))
        index.add_vectors(vectors, ids)
        index.remove_vector(0)
        assert index.total_vectors == 9

    def test_save_load(self, tmp_path):
        index = FaissIndex(dimension=512)
        vectors = np.random.randn(10, 512).astype(np.float32)
        ids = list(range(10))
        index.add_vectors(vectors, ids)
        index_path = str(tmp_path / "test.index")
        id_map_path = str(tmp_path / "test_map.json")
        index.save(index_path, id_map_path)
        new_index = FaissIndex(dimension=512)
        new_index.load(index_path, id_map_path)
        assert new_index.total_vectors == 10
