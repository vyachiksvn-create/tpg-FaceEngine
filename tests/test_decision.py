from __future__ import annotations

import numpy as np
import pytest

from feature.core.decision import DecisionEngine
from feature.config import ConfigManager


class DummySearchConfig:
    merge_strategy = "hybrid"


class DummyRecognitionConfig:
    threshold = 0.6


class DummyConfig:
    search = DummySearchConfig()
    recognition = DummyRecognitionConfig()


class TestDecisionEngine:
    def test_decide_with_candidates(self):
        engine = DecisionEngine(DummyConfig())
        query = np.random.randn(512).astype(np.float32)
        emb = np.random.randn(512).astype(np.float32)
        embeddings_map = {1: emb}
        results = engine.decide(query, [(1, 0.1)], embeddings_map)
        assert isinstance(results.confidence, float)

    def test_decide_no_candidates(self):
        engine = DecisionEngine(DummyConfig())
        query = np.random.randn(512).astype(np.float32)
        results = engine.decide(query, [], {})
        assert results.identity_id is None

    def test_max_strategy(self):
        engine = DecisionEngine(DummyConfig())
        query = np.random.randn(512).astype(np.float32)
        emb1 = np.random.randn(512).astype(np.float32)
        emb2 = np.random.randn(512).astype(np.float32)
        embeddings_map = {1: emb1, 2: emb2}
        results = engine.decide(query, [(1, 0.1), (2, 0.2)], embeddings_map, strategy="max")
        assert results.strategy == "max"

    def test_explain(self):
        engine = DecisionEngine(DummyConfig())
        query = np.random.randn(512).astype(np.float32)
        emb = np.random.randn(512).astype(np.float32)
        results = engine.decide(query, [(1, 0.1)], embeddings_map={1: emb})
        explanation = engine.explain(results)
        assert isinstance(explanation, str)
        assert len(explanation) > 0